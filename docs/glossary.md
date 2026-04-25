# Glossary

## VQA and benchmark terminology

**VQA (Visual Question Answering)** — A task where a model receives an image and a question and must select or generate the correct answer. In BJJ-VQA, the format is multiple-choice with four options.

**Stem** — The question text presented to the model. BJJ-VQA uses two stem formats: COMPLETION (finish the instructor's sentence) and CLASSIFICATION (identify the role or priority of a technique detail).

**Distractor** — A wrong answer option in a multiple-choice question. Good distractors are plausible to someone who trains but incorrect given the specific image and context.

**Stem leak** — When the stem text alone is sufficient to eliminate one or more wrong options, without looking at the image. A question with severe stem leak can be answered by language reasoning alone, making it invalid as a visual benchmark.

**No-image ablation** — Running the eval with images hidden (`bjj_vqa_no_images` task). Questions the model answers correctly without the image are likely suffering from stem leak or are answerable from BJJ knowledge alone.

**Adversarial rubric** — The seven-criterion check (T1-T7) applied to every question before it enters the dataset. Criteria cover stem leak, role coherence, single correct answer, image dependency, image clarity, BJJ correctness, and format compliance.

**HF Community Evals** — The Hugging Face decentralized leaderboard system. Researchers run benchmarks registered as Community Evals using inspect-ai; results are stored in model repos as `.eval_results/` and aggregated on HF leaderboards.

**inspect-ai** — The evaluation framework used by this benchmark. Handles dataset loading, model calls, scoring, and result logging. Supports all major model providers via a uniform API.

**COMPLETION stem** — A stem that ends an instructor's statement and asks which option correctly finishes it. Used when the instructor stated a principle or sequence step directly.

**CLASSIFICATION stem** — A stem that names a technique or detail and asks what role or priority it has. Used when the instructor categorized something (first resort, last resort, only when X, etc.).

**CORRECT option** — The answer option that matches what the instructor taught, stated as a short coaching cue.

**WRONG-CONTEXT option** — A real BJJ principle, but from a different position or goal than what is shown in the image.

**WRONG-MECHANISM option** — Names the right outcome but gives the wrong physical reason for why it works.

**WRONG-DIRECTION option** — States the correct mechanism but reverses the effect (e.g., says "pull" when the correct action is "push").

## BJJ terminology

**Armlock (Juji-gatame)** — A submission that hyperextends the elbow by controlling the arm across the body and applying upward pressure with the hips. One of the most common finishes from guard.

**Closed guard** — A position where the bottom athlete wraps their legs around the opponent's waist and crosses their ankles behind the back. Controls distance and enables sweeps and submissions.

**Knee shield** — A guard variation where one knee is placed in front of the opponent's chest or shoulder to create and maintain distance. Used for guard retention and as a platform for sweeps.

**Loop choke** — A collar choke applied by feeding one arm through the collar while the other arm loops around the opponent's neck. Common from turtle position and guard.

**Guillotine** — A choke applied by wrapping one or both arms around the opponent's neck while they are attempting a takedown or are in turtle position.

**Omoplata** — A shoulder lock applied from guard by trapping the opponent's arm with the legs and rotating to create pressure on the shoulder joint.

**Scissor sweep** — A guard sweep executed by scissoring the legs — one leg pushing into the opponent's hip, one hooking behind their knee — to off-balance them to the side.

**Back take** — Securing a position behind the opponent with both hooks (legs) inside the thighs, enabling chokes and control. One of the highest-value positions in competition.

**Turtle position** — A defensive position where the athlete is on hands and knees with the head tucked. Often a transitional position between guard and back.

**Underhook** — A grip where one arm passes under the opponent's arm and wraps around their body. Provides control and is contested in many positions.

**Overhook** — The opposite of an underhook: the arm passes over the opponent's arm. Used to control the arm and limit their underhook.

**Guard pass** — Moving from inside the opponent's guard to a side or top control position. Requires breaking down the opponent's guard structure.

**Hook** — In back control, a hook is when the attacking athlete's leg is inserted between the opponent's legs with the foot pointing outward to maintain control. Two hooks are needed to establish full back control.

**Lapel grip** — Gripping the lapel (front collar edge) of the opponent's gi jacket. Used to set up chokes and control position in gi grappling.

**Double-leg takedown** — A wrestling takedown where both of the opponent's legs are grabbed to drive them to the mat.

**X-guard** — An open guard position where the bottom athlete sits beneath the opponent and uses both legs — one hooking behind the near leg, one pushing on the far leg — to off-balance and sweep.

**Wrestling for grips** — The process of establishing advantageous hand and arm position before executing a technique. Grip fighting is often the decisive factor in high-level matches.
