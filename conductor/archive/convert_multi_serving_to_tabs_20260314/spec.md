# Specification - Convert Multi-Serving Recipes to Zensical Tabs

## Overview
The goal of this track is to convert identified recipe Markdown files that have multiple "Ingredients" sections (e.g., for different sizes or components) to use Content Tabs (powered by `pymdownx.tabbed`). This will improve the layout, save vertical space, and provide a better user experience by allowing users to switch between different variations of a recipe easily.

## Functional Requirements
1. **Zensical Tabs Implementation:** For each identified recipe, replace multiple "Ingredients" headers with a single "Ingredients" header followed by Content Tabs.
2. **Tab Naming:** Use clear and descriptive names for the tabs (e.g., "9 Inch", "10 Inch", "Dough", "Frosting").
3. **Consistency:** Ensure the tabbed layout follows a consistent style across all converted recipes.
4. **Validation:** Verify that the generated Markdown renders correctly and that the site build passes.

## Non-Functional Requirements
- **Maintainability:** Ensure the Markdown remains easy to read and edit.
- **Performance:** The use of tabs should not negatively impact the page loading or rendering speed.

## Targeted Recipes (From "Identify Multi-Serving Recipes" track)

### High Priority (Alternative Options)
- `docs/desserts/martha-stewarts-new-york-style-cheesecake.md` (9 Inch vs 10 Inch)
- `docs/ingredients/post-baking-glazes/royal-icing.md` (Fresh vs Powdered Egg Whites)

### Other Identified Recipes
- beverages/iced-chai-latte.md
- breads/another-lemon-blueberry-bread.md
- breads/bagels.md
- breads/baguettes.md
- breads/basic-sweet-babka.md
- breads/best-ever-banana-bread.md
- breads/big-and-bubbly-focaccia.md
- breads/brioche.md
- breads/challah.md
- breads/ciabatta.md
- breads/cinnamon-raisin-sourdough-bread.md
- breads/cinnamon-streusel-bread.md
- breads/cranberry-orange-bread.md
- breads/french-bread.md
- breads/gilligan-monkey-bread.md
- breads/grilled-naan.md
- breads/honey-challah-with-assorted-toppings.md
- breads/japanese-milk-bread-rolls.md
- breads/japanese-milk-bread.md
- breads/lemon-bread.md
- breads/naan.md
- breads/pain-aux-raisins.md
- breads/pumpkin-coffee-cake.md
- breads/rosca-de-reyes.md
- breads/sourdough-pretzels.md
- breads/star-bread.md
- breads/texas-roadhouse-rolls.md
- breads/the-best-pumpkin-bread.md
- breads/the-best-sweet-cornbread.md
- breads/vermont-sourdough.md
- breakfast/apple-cider-doughnuts.md
- breakfast/chocolate-muffins.md
- breakfast/cinnamon-rolls.md
- breakfast/conchas-(mexican-pan-dulce).md
- breakfast/dorie-greenspan's-lemon-poppy-muffins.md
- breakfast/french-omelet.md
- breakfast/frittata.md
- breakfast/overnight-oats.md
- breakfast/southwestern-butternut-squash-and-black-bean-breakfast-bowl.md
- breakfast/yeasted-doughnuts-with-chocolate-frosting.md
- breakfast/yeasted-doughnuts.md
- cookies-and-bars/black-and-white-cookies.md
- cookies-and-bars/brookies.md
- cookies-and-bars/brown-butter-and-maple-chewy-pumpkin-cookies.md
- cookies-and-bars/brown-butter-iced-oatmeal-cookies.md
- cookies-and-bars/cherry-bars.md
- cookies-and-bars/cinnamon-spiced-shortbread.md
- cookies-and-bars/cranberry-bars.md
- cookies-and-bars/custard-creams.md
- cookies-and-bars/french-macarons.md
- cookies-and-bars/king-arthur-chocolate-chip-cookies.md
- cookies-and-bars/oreos.md
- cookies-and-bars/peach-bars.md
- cookies-and-bars/peanut-butter-sandwich-cookies.md
- cookies-and-bars/pumpkin-cookies-with-cream-cheese-frosting.md
- cookies-and-bars/salted-caramel-chocolate-macarons.md
- cookies-and-bars/samoas.md
- desserts/brandy-snaps.md
- desserts/cake/apple-cake.md
- desserts/cake/apple-fritter-cake.md
- desserts/cake/boston-cream-pie.md
- desserts/cake/cinnamon-chocolate-cake.md
- desserts/cake/cinnamon-crisp-coffee-cake.md
- desserts/cake/classic-birthday-cake.md
- desserts/cake/dinner-party-yogurt-cake.md
- desserts/cake/funfetti-cake.md
- desserts/cake/grammys-texas-sheet-cake.md
- desserts/cake/gâteau-basque.md
- desserts/cake/hummingbird-cake.md
- desserts/cake/ina-garten's-coconut-cake.md
- desserts/cake/king-arthurs-carrot-cake.md
- desserts/cake/lemon-bundt-cake.md
- desserts/cake/lemon-thyme-yogurt-cake.md
- desserts/cake/marble-cake.md
- desserts/cake/poppy-seed-almond-cake.md
- desserts/cake/prinsesstårta.md
- desserts/cake/reine-be-saba-(queen-of-sheba).md
- desserts/cake/smash-cake.md
- desserts/cake/sour-cream-coffee-cake.md
- desserts/cake/strawberry-cake.md
- desserts/cake/the-original-boston-cream-pie.md
- desserts/cake/tiramisù.md
- desserts/cake/tres-leches-cake-with-berries.md
- desserts/cake/vegan-carrot-cake.md
- desserts/cake/victoria-sandwich-cake.md
- desserts/cake/yule-log-(classic-bûche-de-noël).md
- desserts/chocolate-whoopie-pies-with-vanilla-buttercream-filling.md
- desserts/cooks-illustrated-lemon-bars.md
- desserts/crème-bavaroise.md
- desserts/crêpes-suzette.md
- desserts/cupcakes/white-chocolate-strawberry-cupcakes.md
- desserts/fruit-galette.md
- desserts/gordon-ramsay's-chocolate-soufflé.md
- desserts/ina-garten's-apple-crisp.md
- desserts/melomakarona.md
- desserts/millefeuille.md
- desserts/pie/banoffee-pie.md
- desserts/pie/his-favorite-butterscotch-pie.md
- desserts/pie/lemon-pie.md
- desserts/pie/shoofly-pie.md
- desserts/pie/tart-cherry-pie.md
- desserts/pie/the-best-lemon-meringue-pie.md
- desserts/pumpkin-cheesecake.md
- desserts/sticky-toffee-pudding.md
- desserts/strawberry-rhubarb-crisp.md
- desserts/strawberry-shortcakes.md
- desserts/tarts/cranberry-curd-tart-with-almond-crust.md
- ingredients/frosting/cream-cheese-frosting.md
- ingredients/stiff-sourdough-starter.md
- ingredients/tofu/crispy-baked-peanut-tofu.md
- lunches/sweet-potato-chickpea-buddha-bowl.md
- main/black-bean-corn-and-zucchini-enchiladas.md
- main/eggplant-parmigiana.md
- main/ginger-sesame-vegan-meatballs.md
- main/maria-agresta’s-gnocchi-alla-cilentana.md
- main/pasta-with-burst-cherry-tomato-sauce.md
- main/peruvian-burrito-bowl.md
- main/shallot-onion-and-chive-tart.md
- main/tostadas-with-refried-black-beans-and-pickled-cabbage-and-onion.md
- main/vegetarian-tacos.md
- sides/salads/blueberry-chickpea-salad.md
- sides/salads/tomato-feta-pasta-salad.md
- sides/snacks/fresh-spring-rolls.md
- sides/snacks/strawberry-protein-bites.md
- soups-and-stews/easy-vegan-ramen.md
- soups-and-stews/roasted-tomato-soup.md

## Acceptance Criteria
- [ ] All recipes in the list are converted to use Zensical Content Tabs for their "Ingredients" sections.
- [ ] Each converted page renders correctly with working tabs.
- [ ] The `zensical build` command runs successfully without errors.
