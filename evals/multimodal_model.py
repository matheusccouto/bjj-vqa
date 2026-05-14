"""Multimodal OpenRouter model for DeepEval quality gates.

Subclasses OpenRouterModel to add multimodal (image) support via the
OpenAI-compatible chat completions API used by OpenRouter.
"""

from deepeval.models import OpenRouterModel
from deepeval.models.llms.utils import safe_asyncio_run, trim_and_load_json
from deepeval.test_case import MLLMImage
from deepeval.utils import check_if_multimodal, convert_to_multi_modal_array
from openai.types.chat.chat_completion import ChatCompletion


class MultimodalOpenRouterModel(OpenRouterModel):
    """OpenRouter model with multimodal (image) support."""

    def supports_multimodal(self) -> bool | None:
        return True

    def generate_content(
        self,
        multimodal_input: list[str | MLLMImage] | None = None,
    ) -> list[dict]:
        """Convert multimodal input to OpenAI-compatible content blocks."""
        multimodal_input = [] if multimodal_input is None else multimodal_input
        content: list[dict] = []
        for element in multimodal_input:
            if isinstance(element, str):
                content.append({"type": "text", "text": element})
            elif isinstance(element, MLLMImage):
                if element.url and not element.local:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": element.url},
                        },
                    )
                else:
                    element.ensure_images_loaded()
                    data_uri = f"data:{element.mimeType};base64,{element.dataBase64}"
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": data_uri},
                        },
                    )
        return content

    def _generate_with_content(
        self,
        content: list[dict],
        schema: type | None = None,
    ) -> tuple[str | dict, float]:
        """Generate using pre-built multimodal content blocks."""
        client = self.load_model(async_mode=True)
        return safe_asyncio_run(
            self._a_generate_with_client_and_content(
                client,
                content,
                schema,
            ),
        )

    async def _a_generate_with_client_and_content(
        self,
        client,
        content: list[dict],
        schema: type | None = None,
    ) -> tuple[str | dict, float]:
        """Async generation with pre-built content."""
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

    def generate(
        self,
        prompt: str,
        schema: type | None = None,
    ) -> tuple[str | dict, float]:
        if check_if_multimodal(prompt):
            parsed = convert_to_multi_modal_array(input=prompt)
            content = self.generate_content(parsed)
            return self._generate_with_content(content, schema)
        return super().generate(prompt, schema)

    async def a_generate(
        self,
        prompt: str,
        schema: type | None = None,
    ) -> tuple[str | dict, float]:
        if check_if_multimodal(prompt):
            parsed = convert_to_multi_modal_array(input=prompt)
            content = self.generate_content(parsed)
            client = self.load_model(async_mode=True)
            return await self._a_generate_with_client_and_content(
                client,
                content,
                schema,
            )
        return await super().a_generate(prompt, schema)

    def generate_raw_response(
        self,
        prompt: str,
        top_logprobs: int = 5,
    ) -> tuple[ChatCompletion, float]:
        if check_if_multimodal(prompt):
            parsed = convert_to_multi_modal_array(input=prompt)
            content = self.generate_content(parsed)
            client = self.load_model(async_mode=False)
            completion = client.chat.completions.create(
                model=self.name,
                messages=[{"role": "user", "content": content}],
                temperature=self.temperature,
                logprobs=True,
                top_logprobs=top_logprobs,
                **self.generation_kwargs,
            )
            cost = self.calculate_cost(
                completion.usage.prompt_tokens,
                completion.usage.completion_tokens,
                response=completion,
            )
            return completion, cost
        return super().generate_raw_response(prompt, top_logprobs)

    async def a_generate_raw_response(
        self,
        prompt: str,
        top_logprobs: int = 5,
    ) -> tuple[ChatCompletion, float]:
        if check_if_multimodal(prompt):
            parsed = convert_to_multi_modal_array(input=prompt)
            content = self.generate_content(parsed)
            client = self.load_model(async_mode=True)
            completion = await client.chat.completions.create(
                model=self.name,
                messages=[{"role": "user", "content": content}],
                temperature=self.temperature,
                logprobs=True,
                top_logprobs=top_logprobs,
                **self.generation_kwargs,
            )
            cost = self.calculate_cost(
                completion.usage.prompt_tokens,
                completion.usage.completion_tokens,
                response=completion,
            )
            return completion, cost
        return await super().a_generate_raw_response(prompt, top_logprobs)
