"""Thin multimodal wrapper for OpenRouter in DeepEval.

Overrides ``supports_multimodal`` so DeepEval routes image slugs through
this model, and converts ``[DEEPEVAL:IMAGE:...]`` slugs into OpenAI-compatible
multimodal content blocks before calling the API.

Only ``_generate_with_client`` is overridden — ``generate_raw_response`` is
not, so GEval will fall back to JSON score extraction instead of logprob
weighting. This is acceptable for a 0/1 rubric.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from deepeval.models import OpenRouterModel
from deepeval.models.llms.utils import trim_and_load_json
from deepeval.test_case import MLLMImage
from deepeval.utils import check_if_multimodal, convert_to_multi_modal_array

if TYPE_CHECKING:
    from openai import AsyncOpenAI
    from pydantic import BaseModel


def _to_content_blocks(prompt: str) -> str | list[dict[str, Any]]:
    """Convert a prompt string with image slugs to OpenAI content blocks.

    Returns the original string unchanged if no slugs are present.
    """
    if not check_if_multimodal(prompt):
        return prompt

    parsed = convert_to_multi_modal_array(input=prompt)
    blocks: list[dict[str, Any]] = []
    for element in parsed:
        if isinstance(element, str):
            blocks.append({"type": "text", "text": element})
        elif isinstance(element, MLLMImage):
            if element.url and not element.local:
                blocks.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": element.url},
                    },
                )
            else:
                element.ensure_images_loaded()
                data_uri = f"data:{element.mimeType};base64,{element.dataBase64}"
                blocks.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri},
                    },
                )
    return blocks


class MultimodalOpenRouterModel(OpenRouterModel):
    """OpenRouter model that sends images as native multimodal content."""

    def supports_multimodal(self) -> bool | None:
        """Report multimodal support to DeepEval."""
        return True

    async def _generate_with_client(
        self,
        client: AsyncOpenAI,
        prompt: str,
        schema: type[BaseModel] | None = None,
    ) -> tuple[str | dict, float]:
        """Generate with multimodal content when image slugs are present."""
        content = _to_content_blocks(prompt)
        if isinstance(content, list):
            completion = await client.chat.completions.create(
                model=self.name,
                messages=[{"role": "user", "content": content}],
                temperature=self.temperature,
                **self.generation_kwargs,
            )
            output = completion.choices[0].message.content
            cost = self.calculate_cost(
                completion.usage.prompt_tokens,
                completion.usage.completion_tokens,
                response=completion,
            )
            if schema is not None:
                json_output = trim_and_load_json(output)
                return schema.model_validate(json_output), cost
            return output, cost
        return await super()._generate_with_client(client, prompt, schema)
