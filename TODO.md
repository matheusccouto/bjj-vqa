# BJJ-VQA TODO

## Done ✓

- [x] `eval.yaml` para HuggingFace Community Eval
- [x] Per-category accuracy breakdown (experience_level, category, subject)
- [x] Clarificar licenses (GPL code, CC BY-SA dataset - correto)
- [x] Dataset split (100% test, eval-only - correto)

---

## Easy (code only, no new questions)

### High Priority

- [ ] Adicionar keywords/classifiers ao `pyproject.toml`
- [ ] Expandir test coverage (schema validation, CLI tests)
- [ ] Documentar limitations no README

### Medium Priority

- [ ] Melhorar error messages no CLI
- [ ] Type annotations completas no CLI

---

## Medium (requires research/testing, no new questions)

### High Priority

- [ ] Rodar eval com outros modelos (GPT-4o, Claude, Qwen-VL, LLaVA)
- [ ] Registrar benchmark na lista oficial do HF Community Evals

### Medium Priority

- [ ] Consistency metrics (CaCV, CaQV)
- [ ] Robustness testing (image noise, question paraphrasing)
- [ ] Confusion analysis (identificar systematic errors)

---

## Hard (requires human effort)

### Needs new questions ( você only)

- [ ] Balancear dataset: escapes (1→?), passing (3→?), no_gi (9→?)
- [ ] Expandir advanced level (7→?)
- [ ] Human baseline (BJJ practitioners answering questions)
- [ ] Video extension (clips instead of frames)

### Future considerations

- [ ] `reasoning_type` metadata (perception/mechanics/decision/counterfactual)
- [ ] Expandir question diversity ("why", "identify" questions)

---

## Notes

**Current dataset imbalance**:
- 67% intermediate, 21% beginner, 12% advanced
- 84% gi, 16% no_gi
- escapes: 1, passing: 3 (statistically insignificant)

**Accuracy interpretation**:
- Categories com <5 questões não são estatisticamente significativas
- intermediate accuracy (50%) é mais representativa (38 samples)
- advanced (85.7%) e beginner (75%) têm small sample bias