# BJJ-VQA TODO

## Done ✓

- [x] `eval.yaml` para HuggingFace Community Eval
- [x] Per-category accuracy breakdown (experience_level, category, subject)
- [x] Clarificar licenças (GPL código, CC BY-SA dataset - correto)
- [x] Dataset split (100% test, eval-only - correto)
- [x] pyproject.toml metadata (keywords, classifiers, urls)
- [x] README limitations section
- [x] Expandir cobertura de testes (22 tests: schema + CLI + task)
- [x] Workflow_dispatch para multi-model eval com submission HF
- [x] Melhorar mensagens de erro no CLI
- [x] Type annotations completas no CLI

---

## Easy (code only, no new questions)

(All completed)

---

## Medium (requires research/testing, no new questions)

### High Priority

- [ ] Registrar benchmark na lista oficial do HF Community Evals

### Medium Priority

- [ ] Consistency metrics (CaCV, CaQV)
- [ ] Robustness testing (image noise, question paraphrasing)
- [ ] Confusion analysis (identificar erros sistemáticos)

---

## Hard (requires human effort)

### Needs new questions (você only)

- [ ] Balancear dataset: escapes (1→?), passing (3→?), no_gi (9→?)
- [ ] Expandir advanced level (7→?)
- [ ] Human baseline (practitioners respondendo questions)
- [ ] Video extension (clips instead of frames)

### Future considerations

- [ ] `reasoning_type` metadata (perception/mechanics/decision/counterfactual)
- [ ] Expandir diversidade de questions ("why", "identify" questions)

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