# Implementation Plan: Reorganize Vegetarian Category

## Steps
1. [x] **Audit Recipes:** List all recipes in `cook/vegetarian` and determine their functional target (e.g., `main`, `sides`). e95df0c
2. [x] **Batch Move:** Move `.cook` and image files. ee7df71
3. [x] **Update Metadata:** Update the `.cook` files with the `vegetarian` tag. 0c1ebc4
4. [x] **Update Navigation:** Update the `[[project.nav]]` section in `zensical.toml`. a973387
5. [x] **Validation:** Run `task spellcheck` and verify the build. 532df6a

## Target Mapping
- `Adas Polo (Persian Lentil Rice)` -> `main`
- `Black Bean Burgers` -> `main`
- `California Veggie Wraps` -> `lunches`
- `Caramelized Onion, Spinach, and Sweet Potato Tart` -> `tarts`
- `Cauliflower Green Bean Mac and Cheese` -> `main`
- `Chickpea and Spinach Pancakes` -> `breakfast`
- `Creamy Vegan Polenta with Mushrooms and Kale` -> `main`
- `Crustless Broccoli Quiche` -> `breakfast`
- `Fennel and Potato Cassola` -> `main`
- `Fiesta Salad` -> `sides`
- `Game Changers Oat and Lentil Meatloaf` -> `main`
- `Garlic Chana Dal` -> `main`
- `Greens and Grains Bowls` -> `main`
- `Grilled Tofu with Chimichurri Sauce` -> `main`
- `Indian Spiced Lentil Burgers` -> `main`
- `Italian Sausage with Grits & Tomatoes` -> `main`
- `Jackfruit Curry` -> `main`
- `Jeweled Rice` -> `main`
- `Jose Guevara's Gallo Pinto` -> `breakfast`
- `Lemon Garlic Cauliflower Rice` -> `sides`
- `Lemony Broccoli Salad with Chickpeas & Feta` -> `sides`
- `Lentil and Mushroom Stuffed Peppers and Butternut Squash` -> `main`
- `Lentil Meatballs with Lemon Pesto` -> `main`
- `Lentil Mushroom Stew over Mashed Potatoes` -> `main`
- `Lentil Patties` -> `main`
- `Meat-Free Meat Loaf` -> `main`
- `Meatless Umami Shepherd's Pie` -> `main`
- `Mushroom Barbacoa Bowl` -> `main`
- `Mushroom Paprikash` -> `main`
- `Mushroom Rice Burgers` -> `main`
- `Quinoa and Veggie Power Bowls` -> `main`
- `Ratatouille Provençale` -> `main`
- `Simple Chickpea Masala` -> `main`
- `Slow Cooker Indian-Spiced Chickpeas and Red Potatoes` -> `main`
- `Slow Cooker Red Beans and Rice` -> `main`
- `Slow Cooker Vegetarian Black-Eyed Peas` -> `main`
- `Spicy Cashew Quinoa Salad` -> `sides`
- `Spinach and Feta Filo Pie` -> `main`
- `Spinach Salad with Gorgonzola and Pear` -> `sides`
- `Sprouted Kitchen Lentil & Rice Bowls with Vegetable Kebabs` -> `main`
- `Super Nourishing Beans and Greens` -> `main`
- `Texas Potato Pancakes` -> `main`
- `The Best Vegan Burger` -> `main`
- `The Casado Plate` -> `main`
- `Thyme and White Bean Pot Pies` -> `main`
- `Tortilla de Patatas` -> `sides`
- `Vegan Baked Beans` -> `sides`
- `Vegan Caesar Salad` -> `sides`
- `Vegan Giant Bean & Kale Penne` -> `main`
- `Vegan Kale Caesar with Crispy Chickpeas` -> `sides`
- `Vegan Ricotta & Sun-Dried Tomato Pesto Salad` -> `sides`
- `Vegan Tourtiere` -> `main`
- `Vegan Zucchini Lasagna` -> `main`
- `Vegetable Casserole` -> `sides`
- `Vegetarian Pot Pie` -> `main`
- `Veggie Burgers` -> `main`
- `Veggie Cassola` -> `main`
- `Zesty Roasted Vegetables` -> `sides`
- `Zucchini Pasta with Lentil Bolognese` -> `main`
