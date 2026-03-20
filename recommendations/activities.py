ACTIVITIES: dict = {
    "number": {
        1: (
            "Practice counting, reading, and writing numbers up to 1,000. "
            "Use number lines to compare values. Try place value charts for ones, tens, hundreds. "
            "Khan Academy: 'Place value' (Grade 3–4 level). No internet: use stones or seeds to build numbers."
        ),
        2: (
            "Practise adding and subtracting 3-digit numbers with regrouping. "
            "Introduce fractions using drawings (half a mango, a quarter of a circle). "
            "Khan Academy: 'Addition and subtraction' and 'Intro to fractions'."
        ),
        3: (
            "Work on converting between fractions, decimals and percentages. "
            "Solve ratio and proportion word problems from everyday market situations. "
            "Khan Academy: 'Ratios and proportions' (Grade 6). "
            "Activity: calculate discounts on market prices using percentages."
        ),
        4: (
            "Extend to operations with negative numbers and explore number patterns. "
            "Challenge: investigate prime factorisation and LCM/GCF applications. "
            "CK-12: 'Number Theory' unit."
        ),
    },
    "algebra": {
        1: (
            "Identify number patterns (add 2, multiply by 3). Complete missing number sequences. "
            "EGMA-style: find the missing number in: 5, 10, ___, 20. "
            "No internet: create your own pattern cards and swap with a classmate."
        ),
        2: (
            "Practise evaluating simple expressions like 2n + 3 for given values of n. "
            "Solve one-step equations: x + 5 = 12, 3y = 21. "
            "Khan Academy: 'Variables and expressions' (Grade 6)."
        ),
        3: (
            "Solve two-step equations and write algebraic expressions from word problems. "
            "Explore patterns that lead to generalisation: e.g., area of rectangles as l × w. "
            "Khan Academy: 'Equations and inequalities' (Grade 7)."
        ),
        4: (
            "Explore simultaneous equations graphically and algebraically. "
            "Create algebraic models for real-world situations such as crop yield prediction. "
            "CK-12: 'Linear Equations' unit."
        ),
    },
    "geometry_measurement": {
        1: (
            "Identify and name basic 2D shapes: triangle, rectangle, circle, square. "
            "Practise measuring lengths with a ruler in centimetres and metres. "
            "No internet: use a string to measure the perimeter of objects in the classroom."
        ),
        2: (
            "Calculate area and perimeter of rectangles and squares. "
            "Identify parallel and perpendicular lines and types of angles. "
            "Khan Academy: 'Area and perimeter' (Grade 4–5)."
        ),
        3: (
            "Calculate area of triangles and composite shapes. "
            "Explore transformations: reflection, rotation, translation on grid paper. "
            "Khan Academy: 'Geometry' (Grade 7). "
            "Activity: draw a map of the school compound using grid paper."
        ),
        4: (
            "Explore circles (circumference, area using π). "
            "Apply coordinate geometry to describe positions and transformations. "
            "CK-12: 'Geometry' chapter on circles and coordinates."
        ),
    },
    "handling_data": {
        1: (
            "Collect simple data and record it in a tally chart or table. "
            "Read a basic bar chart to answer questions. "
            "No internet: survey classmates about their favourite fruit and draw a bar chart."
        ),
        2: (
            "Calculate mean (average) from a small data set. "
            "Interpret bar charts and pictograms. Introduce the idea of likely and unlikely events. "
            "Khan Academy: 'Statistics and probability' (Grade 5–6)."
        ),
        3: (
            "Compare data sets using mean, median, and mode. "
            "Calculate simple probabilities as fractions (e.g., drawing a red ball from a bag). "
            "Khan Academy: 'Basic probability' (Grade 7)."
        ),
        4: (
            "Design surveys, collect data, and present findings using multiple chart types. "
            "Explore compound events and experimental vs. theoretical probability. "
            "CK-12: 'Probability and Statistics' unit."
        ),
    },
    "diversity_matter": {
        1: (
            "Learn the properties of common materials: metals, wood, plastic, glass. "
            "Understand that all living things are made of cells. "
            "No internet: sort classroom objects into groups based on material properties."
        ),
        2: (
            "Compare properties of materials and explain why they are used for certain purposes. "
            "Identify the main parts of a plant cell and an animal cell. "
            "Khan Academy: 'Biology' → 'Cells'. CK-12: 'Cell structure and function'."
        ),
        3: (
            "Investigate how materials change when heated or cooled (reversible vs. irreversible changes). "
            "Explore specialised cells and their functions. "
            "Activity: design an experiment to test which material absorbs most water."
        ),
        4: (
            "Study mixtures, solutions, and separation techniques. "
            "Explore cell division and its role in growth and repair. "
            "CK-12: 'Chemistry of Life' and 'Cell Division' units."
        ),
    },
    "cycles": {
        1: (
            "Learn the water cycle stages: evaporation, condensation, precipitation. "
            "Identify the main stages of a plant's life cycle. "
            "No internet: draw and label the water cycle diagram."
        ),
        2: (
            "Compare life cycles of different organisms (butterfly, frog, maize plant). "
            "Discuss the importance of crop rotation and basic soil care for farming. "
            "Khan Academy: 'Biology' → 'Life cycles'. Activity: germinate seeds and record daily growth."
        ),
        3: (
            "Explain how the seasons and rainfall patterns affect crop production in Ghana. "
            "Analyse conditions for healthy livestock (nutrition, disease prevention, shelter). "
            "Activity: interview a local farmer about seasonal farming practices."
        ),
        4: (
            "Investigate the carbon and nitrogen cycles and their role in ecosystems. "
            "Research sustainable farming techniques used in Ghana. "
            "CK-12: 'Biogeochemical Cycles' unit."
        ),
    },
    "systems": {
        1: (
            "Identify the major organ systems of the human body and their main functions. "
            "Name the planets in the Solar System and describe day/night and seasons. "
            "No internet: draw and label a diagram of the human digestive system."
        ),
        2: (
            "Explain how body systems work together (digestive + circulatory). "
            "Describe food chains and food webs in a local ecosystem. "
            "Khan Academy: 'Biology' → 'Human body systems'. "
            "Activity: create a food web using animals found near the school."
        ),
        3: (
            "Analyse the impact of removing one species from a food web. "
            "Describe how farming systems interact with local ecosystems. "
            "NGSS practice: plan and carry out an investigation on local soil or plant samples."
        ),
        4: (
            "Evaluate how human activities affect ecosystem balance. "
            "Explore space exploration and its relevance to Earth science. "
            "CK-12: 'Ecosystems' and 'The Solar System' units."
        ),
    },
    "forces_energy": {
        1: (
            "Identify forms of energy: light, heat, sound, electrical, kinetic. "
            "Understand what a complete electrical circuit requires. "
            "No internet: build a simple circuit with a battery, wire, and bulb (if available)."
        ),
        2: (
            "Explain common energy conversions: solar panel (light → electrical), wood fire (chemical → heat). "
            "Identify conductors and insulators and explain their uses. "
            "Khan Academy: 'Physics' → 'Energy'. Activity: test which materials conduct electricity."
        ),
        3: (
            "Apply the principle of conservation of energy to everyday situations. "
            "Analyse data from an energy experiment and identify patterns. "
            "NGSS practice: interpret a graph of temperature vs. time during heating."
        ),
        4: (
            "Investigate renewable vs. non-renewable energy sources and their environmental impact. "
            "Design a simple energy solution for a community problem (e.g., solar lantern). "
            "CK-12: 'Energy and Forces' unit."
        ),
    },
    "humans_environment": {
        1: (
            "Understand the importance of waste sorting: biodegradable vs. non-biodegradable. "
            "Identify basic disease prevention methods: handwashing, safe water, mosquito nets. "
            "No internet: create a poster about proper waste disposal for the school compound."
        ),
        2: (
            "Explain how deforestation and pollution affect local communities. "
            "Describe multiple strategies for preventing common diseases in Ghana (malaria, cholera). "
            "Khan Academy: 'Health and medicine'. Activity: map environmental hazards near the school."
        ),
        3: (
            "Analyse the causes and effects of climate change with local examples. "
            "Evaluate evidence: distinguish between factual claims and opinions about environmental issues. "
            "PISA-style activity: read a newspaper article about flooding and identify evidence vs. opinion."
        ),
        4: (
            "Design a green economy solution for a local problem (composting, tree planting, solar drying). "
            "Evaluate the long-term impact of human activities using data and evidence. "
            "CK-12: 'Human Impact on the Environment' unit."
        ),
    },
}


def get_recommendations(scores: dict) -> dict:
    return {domain: ACTIVITIES[domain][ds["level"]] for domain, ds in scores.items() if domain in ACTIVITIES}


def get_priority_gaps(scores: dict) -> list:
    gaps = [(domain, ds["score"]) for domain, ds in scores.items() if ds["level"] <= 2]
    return [domain for domain, _ in sorted(gaps, key=lambda x: x[1])]
