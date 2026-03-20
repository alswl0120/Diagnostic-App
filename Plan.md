# Basic Diagnostic App — Project Plan

## 1. Overview

**Target:** Ghana Junior High School Grade 1 (JHS1) students
**Actual learning level:** Elementary school (early grades) — significant foundational gaps
**Purpose:** Rapidly diagnose learning levels in Mathematics and Science; identify learning-deficit and slow-learning students; guide each student to appropriate next learning activities
**Platform:** Enumalabs (Docker + Streamlit), deployed at `basic-diagnostic.enumalabs.com`
**Time limit:** ~28 minutes (Mathematics 13 min + Science 15 min)

---

## 2. Assessment Design Basis

This assessment is **not a test**. It is a diagnostic tool that maps each student's current performance to four learning levels and recommends appropriate next steps.

Assessment frameworks used as **methodology references** (item design, cognitive levels, scoring criteria):

| Framework | Role in this app |
|---|---|
| **EGMA** (Early Grade Mathematics Assessment) | Number operations item design; foundational numeracy progression; skip-counting and word problem structure |
| **TIMSS 2027** | Cognitive domain levels: Knowing → Applying → Reasoning; domain weighting and item format |
| **PISA 2025 Science** | Higher-order science items: Explain phenomena scientifically; Evaluate evidence; Real-world context |
| **NGSS** | Science and Engineering Practices: Data interpretation, argumentation from evidence, investigation design |

---

## 3. Curriculum Alignment — Ghana JHS1

All assessment domains are **directly mapped to Ghana JHS1 official curriculum Strands**.

### Mathematics (13 min, 20 items)

| Domain Key | Label | Ghana Strand | Sub-strands Covered | Items |
|---|---|---|---|---|
| `number` | Number | NUMBER | Number and Numeration Systems, Number Operations, Fractions/Decimals/Percentages, Ratios and Proportion | 6 |
| `algebra` | Algebra | ALGEBRA | Patterns and Relations, Algebraic Expressions, Variables and Equations | 5 |
| `geometry_measurement` | Geometry & Measurement | GEOMETRY AND MEASUREMENT | Shape and Space, Measurement, Position and Transformation | 5 |
| `handling_data` | Handling Data | HANDLING DATA | Data, Chance or Probability | 4 |

**Total: 4 domains, 20 items**

### Science (15 min, 18 items)

| Domain Key | Label | Ghana Strand | Sub-strands Covered | Items |
|---|---|---|---|---|
| `diversity_matter` | Diversity of Matter | DIVERSITY OF MATTER | Materials, Living Cells | 3 |
| `cycles` | Cycles | CYCLES | Earth Science, Life Cycle of Organisms, Crop Production, Animal Production | 4 |
| `systems` | Systems | SYSTEMS | The Human Body System, The Solar System, Ecosystem, Farming Systems | 4 |
| `forces_energy` | Forces and Energy | FORCES AND ENERGY | Energy, Electricity and Electronics, Conversion and Conservation of Energy | 4 |
| `humans_environment` | Humans and the Environment | HUMANS AND THE ENVIRONMENT | Force and Motion, Waste Management, Human Health, Climate Change and Green Economy | 3 |

**Total: 5 domains, 18 items**

---

## 4. Item Design Principles

- **Format:** 4-option multiple choice only (no free text — reduces typing burden on low-spec devices)
- **Difficulty:** Each domain contains items at 3 difficulty levels (1 easy → 2 medium → 3 harder), presented in ascending order
- **Context:** Items use culturally relevant contexts for Ghana (mango farmers, yam harvests, malaria prevention, Ghanaian names)
- **Language:** Plain English at approximately Grade 5–6 reading level
- **No images in v1.0:** Minimises bandwidth requirements; `image_path` field reserved for future versions
- **Assessment framing:** Questions are neutral and factual — no trick questions, no time pressure within items

---

## 5. Scoring and Level Classification

### Domain Score

```
score = correct_answers / total_items_in_domain
skipped items = 0 (counted as incorrect)
```

### Level Classification

| Score Range | Level | Label | Interpretation |
|---|---|---|---|
| 0.00 – 0.40 | 1 | Emerging | Foundational gaps; requires immediate targeted support |
| 0.41 – 0.60 | 2 | Developing | Partial understanding; needs guided practice |
| 0.61 – 0.80 | 3 | Proficient | Solid understanding of core concepts |
| 0.81 – 1.00 | 4 | Advanced | Strong mastery; ready for extension challenges |

### Overall Level

```
overall_score = mean of all 9 domain scores
overall_level = classify_level(overall_score)
```

### Learning Gap Identification

- Domains where **level ≤ 2** are flagged as **Priority Learning Areas**
- Sorted by score ascending (most critical first)
- Drive the recommendations section and PDF report

---

## 6. Application Flow

```
Student arrives → Home page (enter name)
  → Mathematics Assessment (20 questions, ~13 min)
  → Science Assessment (18 questions, ~15 min)
  → Results page (domain scores, level badges, recommended activities)
  → PDF download (individual report)

Teacher view → Dashboard (class averages, per-student breakdown, CSV export)
```

---

## 7. Recommendations Engine

Each of the 9 domains has 4 level-specific activity descriptions (36 total).
Activities are designed to be:
- Accessible without internet (paper-based fallback described)
- Linked to free online resources where available (Khan Academy, CK-12)
- Explicitly connected to Ghana JHS1 Sub-strand content

---

## 8. Infrastructure

| Concern | Solution |
|---|---|
| Persistence | SQLite at `/app/storage/data.db` (WAL mode, survives redeployment) |
| Authentication | Enumalabs Gateway headers (`X-User-Id`, `X-User-Email`, `X-User-Roles`) |
| Teacher access | `X-User-Roles` contains `staff` or `teacher` |
| PDF generation | ReportLab, built-in Helvetica fonts only (no system font install) |
| Offline-friendly | No external CDN; all assets in Docker image; minimal JavaScript |
| Low-bandwidth | No images in items; Streamlit server-side rendering; `st.bar_chart` only |

---

## 9. Testing

All core modules developed using Test-Driven Development (TDD):

| Test File | Module Tested |
|---|---|
| `tests/test_scoring.py` | `core/scoring.py` — level classification, domain/section scoring |
| `tests/test_database.py` | `core/database.py` — CRUD, WAL, domain averages |
| `tests/test_auth.py` | `core/auth.py` — header parsing, teacher detection |
| `tests/test_loader.py` | `assessment/loader.py` — JSON loading, domain grouping |
| `tests/test_session.py` | `assessment/session.py` — response tracking, index mapping |
| `tests/test_recommendations.py` | `recommendations/activities.py` — gap detection, activity lookup |
| `tests/test_pdf_generator.py` | `report/pdf_generator.py` — PDF validity, student name presence |

Run tests:
```bash
cd apps/basic-diagnostic
uv run pytest tests/ -v --cov=core --cov=assessment --cov=report --cov=recommendations
```

---

## 10. Future Improvements (v2.0)

- Multilingual support (Twi, French for Francophone neighbouring countries)
- Image-based items for geometry domain
- Adaptive item selection (skip easy items if student answers correctly)
- Teacher annotation of individual student reports
- Export to national education management systems
