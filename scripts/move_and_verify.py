import os
import shutil

# Precisely map Cook files to subcategories
sides_mapping = {
    "potatoes": [
        "America's Test Kitchen Best Baked Potatoes", "America's Test Kitchen Best Baked Sweet Potatoes",
        "Amish Potato Salad", "Cheesy Potatoes", "Crispy Herbes de Provence Potatoes", "French Potato Salad",
        "Funeral Potatoes", "Greek Style Lemon Roasted Potatoes", "Hash Browns", "Internet-Famous Crispy Potatoes",
        "Joel Robuchons Mashed Potatoes", "Julia Child's Garlic Mashed Potatoes", "Loaded Vegan Potato Skins",
        "Mom's Potatoes", "Pommes Dauphine", "Pommes Mont D'or", "Potato Au Gratin", "Potato Salad", "Scalloped Potatoes",
        "Tater Tots", "The Best Crispy Roast Potatoes Ever Recipe", "Vegan Mashed Potatoes"
    ],
    "vegetables": [
        "Asparagus Purée", "Braised Asparagus with Lemon and Chives", "Brown Sugar and Spice Roasted Carrots",
        "Brussels Sprouts With Warm Honey Glaze", "Buffalo-Baked Baby Carrots", "Butter-Basted Grilled Mushrooms",
        "Cauliflower Purée with Thyme", "Charred Brussels Sprouts with Walnuts & Gorgonzola", "Creamed Spinach",
        "Fried Green Tomatoes", "Garlic and Lemon Roasted Romanesco Cauliflower", "Garlic Mushrooms",
        "Grilled Mushrooms with Rosemary-Lemon Basting Butter", "Grilled Sweet Potatoes with Chimichurri",
        "Hasselback Roasted Zucchini", "Honey Glazed Carrots and Parsnips", "Ina Garten's Parmesan Roasted Broccoli",
        "Kale Chips", "Kickstarter Garlic Mushrooms", "Kickstarter Lemony Roasted Cauliflower",
        "Maple Harissa Glazed Sweet Potatoes", "Maple Roasted Brussels Sprouts with Pumpkin Seeds",
        "Maple Roasted Carrots with Tahini and Pomegranate", "Mashed Sweet Potatoes with Caramelized Shallots",
        "Miso-Glazed Bok Choy", "Miso-Glazed Carrots", "Mushroom Medley", "Parsnip Purée", "Pea Purée",
        "Roasted Delicata Squash", "Roasted Fennel with Garlic and Thyme", "Sautéed Mushrooms",
        "Skillet-Steamed Haricots Verts", "Spicy Garlic Edamame", "Steamed Broccoli with Vinaigrette",
        "Vegetable Casserole", "Zesty Roasted Vegetables"
    ],
    "grains-and-legumes": [
        "Basmati Pilaf", "Black Beans", "Black Eyed Peas and Greens", "Brazilian Rice", "Corn Tortillas", "Couscous",
        "Garlic Rice", "Gracias Madre Black Beans", "Green Rice", "Pearl Couscous", "Quinoa", "Refried Black Beans"
    ],
    "salads": [
        "Andrew Kings Pasta Salad", "Balsamic-Dressed Cucumber with Olives", "Beach Day Chickpea Salad",
        "Blueberry Chickpea Salad", "Fiesta Salad", "Lemony Broccoli Salad with Chickpeas & Feta", "Macaroni Salad",
        "Mexican Coleslaw", "Pasta Salad", "Red Cabbage Salad", "Spicy Cashew Quinoa Salad",
        "Spinach Salad with Gorgonzola and Pear", "Three-Bean Salad", "Tomato Feta Pasta Salad", "Tomato Salad",
        "Vegan Caesar Salad", "Vegan Kale Caesar with Crispy Chickpeas", "Vegan Ricotta & Sun-Dried Tomato Pesto Salad"
    ],
    "snacks": [
        "Banana Chips", "Bow Tie Pasta Chips", "Carrot Cake Protein Bites", "Carrot Slaw", "Cheese Soufflé",
        "Cheesy Popcorn", "Club Crackers", "Deviled Eggs", "Dried Fruit and Nut Mix", "Falafel Scones with Harissa Yogurt",
        "Fennel and Potato Cassola", "Granola Bars", "Honey and Walnut Baked Brie", "Honey Roasted Peanuts",
        "Kettle Corn", "No Bake Sunshine Energy Bites", "Peanut Butter Bites", "Peanut Butter Chocolate Chip Protein Bites",
        "Pickled Red Onions", "Ritz Crackers", "Roasted Chickpea Snack", "Rosemary Roasted Cashews",
        "Scottish Oatcakes", "Strawberry Protein Bites", "Unsweetened Applesauce"
    ]
}

sauces_mapping = {
    "vinaigrettes": [
        "All-Purpose Vinaigrette", "Broccoli Salad Dressing", "Cilantro Dressing", "Citrus Honey Dressing",
        "Creamy Cilantro Dressing", "French Dressing", "Honey Mustard Vinaigrette", "Hummus-Orange Juice Dressing",
        "Ina Garten's Perfect Vinaigrette", "Italian Vinaigrette", "Jane's 3, 2, 1 Salad Dressing",
        "Orange Juice-Lime Salad Dressing", "Pizzeria Vinaigrette", "Red Wine Vinaigrette", "Rip's Salad Dressing",
        "Roasted Red Pepper Dressing", "Strawberry Tarragon Dressing", "Sumac Lemon Vinaigrette", "Vinaigrette"
    ],
    "salsas": [
        "Aaron Combs' Salsa", "Pumpkin Seed Salsa", "Salsa Brava", "Salsa Fresca (Pico de Gallo)", "Salsa Macha",
        "Salsa Negra", "Salsa Ranchera", "Salsa Roja", "Salsa Verde", "Sweet-and-Spicy Corn Salsa"
    ],
    "dips-and-spreads": [
        "Aji Verde", "Balsamic Onion Jam", "Beet Hummus", "Benedictine Sandwich Spread", "Blue Cheese Herb Spread",
        "Cashew Chipotle Ranch Dressing", "Cashew Crema", "Cashew Nacho Cheese", "Cashew Queso Blanco",
        "Chipotle Mayonnaise", "Chipotle Ranch Dressing", "Claire's Five-Onion Dip", "Edamame Hummus",
        "Green Goddess Dressing", "Hearts of Palm Ceviche", "Homemade Ranch Dip", "Hummus", "Mayonnaise",
        "Mexicrema Dressing", "Oil-Free Easy French Hummus Dressing", "Oil-Free Hummus",
        "Persian Yogurt Dip with Shallots (Mast-O Musir)", "Ranch Dip", "Ranch Dressing", "Roasted Garlic Hummus",
        "Spinach Dip", "Tahini", "Tofu Mayonnaise", "Tzatziki Dip", "Tzatziki Sauce", "Vegan Caesar Dressing",
        "Vegan Chipotle Ranch Dressing", "Vegan Ranch Dressing", "Vegan Sour Cream", "Whipped Almond Ricotta"
    ],
    "sweet-sauces": [
        "Berry Sauce", "Crème Anglaise", "Hot Fudge Sauce", "Mixed Berry Coulis", "Salted Caramel Sauce",
        "Simple Berry Compote", "Single Jar of Fruit Jam", "Sweet-and-Spicy Ketchup"
    ],
    "gravy-and-savory-sauces": [
        "Adobo Sauce", "Alfredo Sauce", "Applied Homemade Vegetarian Gravy", "Arrabbiata Sauce",
        "Asian Sweet-and-Sour Sauce", "A Very Popular BBQ Sauce", "Buffalo Sauce", "Butternut Squash Sauce",
        "Carrot-Tamarind Chutney", "Chilero Hot Sauce", "Chimichurri", "Classic Mustard", "Classic Tartar Sauce",
        "Creamy Peanut Tofu Marinade", "Creamy Vegan Cheese Sauce", "Dijon Mustard", "Enchilada Sauce",
        "Garlic Aioli", "Homemade Chilli Oil", "Honey Mustard Dipping Sauce", "Lebanese Garlic Sauce (Toum)",
        "Magnolia Ranchero Sauce", "Maple Soy Tofu Marinade", "Marinara Sauce", "Miso Glaze", "Mushroom Gravy",
        "Mushroom Sauce", "New York-Style Pizza Sauce", "New York Times' Classic Marinara Sauce",
        "Peanut Dipping Sauce", "Pumpkin Curry Sauce", "Roasted Red Pepper Coulis", "Roasted Red Pepper Sauce",
        "Simple Barbecue Sauce", "Simple Tartar Sauce", "Spaghetti Sauce", "Special Sauce for Burgers",
        "Spicy Vegan Mayo", "Thai Red Curry Tofu Marinade", "The Soyfoods Council Chimichurri",
        "Tomato Ragu", "Tomato Sauce", "Vegetarian Sausage Gravy", "White Mac and Cheese Sauce"
    ]
}

# Markdown mapping based on actual filenames found
sides_md = {
    "potatoes": [
        "america's-test-kitchen-best-baked-potatoes.md", "america's-test-kitchen-best-baked-sweet-potatoes.md",
        "amish-potato-salad.md", "cheesy-potatoes.md", "crispy-herbes-de-provence-potatoes.md",
        "french-potato-salad.md", "funeral-potatoes.md", "greek-style-lemon-roasted-potatoes.md",
        "hash-browns.md", "internet-famous-crispy-potatoes.md", "joel-robuchons-mashed-potatoes.md",
        "julia-child's-garlic-mashed-potatoes.md", "loaded-vegan-potato-skins.md", "mom's-potatoes.md",
        "pommes-dauphine.md", "pommes-mont-d'or.md", "potato-au-gratin.md", "potato-salad.md",
        "scalloped-potatoes.md", "tater-tots.md", "the-best-crispy-roast-potatoes-ever-recipe.md",
        "vegan-mashed-potatoes.md"
    ],
    "vegetables": [
        "asparagus-purée.md", "braised-asparagus-with-lemon-and-chives.md", "brown-sugar-and-spice-roasted-carrots.md",
        "brussels-sprouts-with-warm-honey-glaze.md", "buffalo-baked-baby-carrots.md", "butter-basted-grilled-mushrooms.md",
        "cauliflower-purée-with-thyme.md", "charred-brussels-sprouts-with-walnuts-&-gorgonzola.md",
        "creamed-spinach.md", "fried-green-tomatoes.md", "garlic-and-lemon-roasted-romanesco-cauliflower.md",
        "garlic-mushrooms.md", "grilled-mushrooms-with-rosemary-lemon-basting-butter.md",
        "grilled-sweet-potatoes-with-chimichurri.md", "hasselback-roasted-zucchini.md", "honey-glazed-carrots-and-parsnips.md",
        "ina-garten's-parmesan-roasted-broccoli.md", "kale-chips.md", "kickstarter-garlic-mushrooms.md",
        "kickstarter-lemony-roasted-cauliflower.md", "maple-harissa-glazed-sweet-potatoes.md",
        "maple-roasted-brussels-sprouts-with-pumpkin-seeds.md", "maple-roasted-carrots-with-tahini-and-pomegranate.md",
        "mashed-sweet-potatoes-with-caramelized-shallots.md", "miso-glazed-bok-choy.md", "miso-glazed-carrots.md",
        "mushroom-medley.md", "parsnip-purée.md", "pea-purée.md", "roasted-delicata-squash.md",
        "roasted-fennel-with-garlic-and-thyme.md", "sautéed-mushrooms.md", "skillet-steamed-haricots-verts.md",
        "spicy-garlic-edamame.md", "steamed-broccoli-with-vinaigrette.md", "vegetable-casserole.md", "zesty-roasted-vegetables.md"
    ],
    "grains-and-legumes": [
        "basmati-pilaf.md", "black-beans.md", "black-eyed-peas-and-greens.md", "brazilian-rice.md", "corn-tortillas.md",
        "couscous.md", "garlic-rice.md", "gracias-madre-black-beans.md", "green-rice.md", "pearl-couscous.md",
        "quinoa.md", "refried-black-beans.md"
    ],
    "salads": [
        "andrew-kings-pasta-salad.md", "balsamic-dressed-cucumber-with-olives.md", "beach-day-chickpea-salad.md",
        "blueberry-chickpea-salad.md", "fiesta-salad.md", "lemony-broccoli-salad-with-chickpeas-&-feta.md",
        "macaroni-salad.md", "mexican-coleslaw.md", "pasta-salad.md", "red-cabbage-salad.md", "spicy-cashew-quinoa-salad.md",
        "spinach-salad-with-gorgonzola-and-pear.md", "three-bean-salad.md", "tomato-feta-pasta-salad.md",
        "tomato-salad.md", "vegan-caesar-salad.md", "vegan-kale-caesar-with-crispy-chickpeas.md",
        "vegan-ricotta-&-sun-dried-tomato-pesto-salad.md"
    ],
    "snacks": [
        "banana-chips.md", "bow-tie-pasta-chips.md", "carrot-cake-protein-bites.md", "carrot-slaw.md", "cheese-soufflé.md",
        "cheesy-popcorn.md", "club-crackers.md", "deviled-eggs.md", "dried-fruit-and-nut-mix.md",
        "falafel-scones-with-harissa-yogurt.md", "fennel-and-potato-cassola.md", "granola-bars.md",
        "honey-and-walnut-baked-brie.md", "honey-roasted-peanuts.md", "kettle-corn.md", "no-bake-sunshine-energy-bites.md",
        "peanut-butter-bites.md", "peanut-butter-chocolate-chip-protein-bites.md", "pickled-red-onions.md",
        "ritz-crackers.md", "roasted-chickpea-snack.md", "rosemary-roasted-cashews.md", "scottish-oatcakes.md",
        "strawberry-protein-bites.md", "unsweetened-applesauce.md", "kroket.md"
    ]
}

sauces_md = {
    "vinaigrettes": [
        "all-purpose-vinaigrette.md", "broccoli-salad-dressing.md", "cilantro-dressing.md", "citrus-honey-dressing.md",
        "creamy-cilantro-dressing.md", "french-dressing.md", "honey-mustard-vinaigrette.md", "hummus-orange-juice-dressing.md",
        "ina-garten's-perfect-vinaigrette.md", "italian-vinaigrette.md", "jane's-3,-2,-1-salad-dressing.md",
        "orange-juice-lime-salad-dressing.md", "pizzeria-vinaigrette.md", "red-wine-vinaigrette.md", "rip's-salad-dressing.md",
        "roasted-red-pepper-dressing.md", "strawberry-tarragon-dressing.md", "sumac-lemon-vinaigrette.md", "vinaigrette.md"
    ],
    "salsas": [
        "aaron-combs'-salsa.md", "pumpkin-seed-salsa.md", "salsa-brava.md", "salsa-fresca-(pico-de-gallo).md", "salsa-macha.md",
        "salsa-negra.md", "salsa-ranchera.md", "salsa-roja.md", "salsa-verde.md", "sweet-and-spicy-corn-salsa.md"
    ],
    "dips-and-spreads": [
        "aji-verde.md", "balsamic-onion-jam.md", "beet-hummus.md", "benedictine-sandwich-spread.md", "blue-cheese-herb-spread.md",
        "cashew-chipotle-ranch-dressing.md", "cashew-crema.md", "cashew-nacho-cheese.md", "cashew-queso-blanco.md",
        "chipotle-mayonnaise.md", "chipotle-ranch-dressing.md", "claire's-five-onion-dip.md", "edamame-hummus.md",
        "green-goddess-dressing.md", "hearts-of-palm-ceviche.md", "homemade-ranch-dip.md", "hummus.md", "mayonnaise.md",
        "mexicrema-dressing.md", "oil-free-easy-french-hummus-dressing.md", "oil-free-hummus.md",
        "persian-yogurt-dip-with-shallots-(mast-o-musir).md", "ranch-dip.md", "ranch-dressing.md", "roasted-garlic-hummus.md",
        "spinach-dip.md", "tahini.md", "tofu-mayonnaise.md", "tzatziki-dip.md", "tzatziki-sauce.md", "vegan-caesar-dressing.md",
        "vegan-chipotle-ranch-dressing.md", "vegan-ranch-dressing.md", "vegan-sour-cream.md", "whipped-almond-ricotta.md"
    ],
    "sweet-sauces": [
        "berry-sauce.md", "crème-anglaise.md", "hot-fudge-sauce.md", "mixed-berry-coulis.md", "salted-caramel-sauce.md",
        "simple-berry-compote.md", "single-jar-of-fruit-jam.md", "sweet-and-spicy-ketchup.md"
    ],
    "gravy-and-savory-sauces": [
        "adobo-sauce.md", "alfredo-sauce.md", "applied-homemade-vegetarian-gravy.md", "arrabbiata-sauce.md",
        "asian-sweet-and-sour-sauce.md", "a-very-popular-bbq-sauce.md", "buffalo-sauce.md", "butternut-squash-sauce.md",
        "carrot-tamarind-chutney.md", "chilero-hot-sauce.md", "chimichurri.md", "classic-mustard.md", "classic-tartar-sauce.md",
        "creamy-peanut-tofu-marinade.md", "creamy-vegan-cheese-sauce.md", "dijon-mustard.md", "enchilada-sauce.md",
        "garlic-aioli.md", "homemade-chilli-oil.md", "honey-mustard-dipping-sauce.md", "lebanese-garlic-sauce-(toum).md",
        "magnolia-ranchero-sauce.md", "maple-soy-tofu-marinade.md", "marinara-sauce.md", "miso-glaze.md", "mushroom-gravy.md",
        "mushroom-sauce.md", "new-york-style-pizza-sauce.md", "new-york-times'-classic-marinara-sauce.md",
        "peanut-dipping-sauce.md", "pumpkin-curry-sauce.md", "roasted-red-pepper-coulis.md", "roasted-red-pepper-sauce.md",
        "simple-barbecue-sauce.md", "simple-tartar-sauce.md", "spaghetti-sauce.md", "special-sauce-for-burgers.md",
        "spicy-vegan-mayo.md", "thai-red-curry-tofu-marinade.md", "the-soyfoods-council-chimichurri.md",
        "tomato-ragu.md", "tomato-sauce.md", "vegetarian-sausage-gravy.md", "white-mac-and-cheese-sauce.md"
    ]
}

def move_cook_files(base_dir, mapping):
    for subcat, recipes in mapping.items():
        subcat_dir = os.path.join(base_dir, subcat)
        os.makedirs(subcat_dir, exist_ok=True)
        for recipe in recipes:
            for ext in ['.cook', '.jpg', '.png']:
                src = os.path.join(base_dir, f"{recipe}{ext}")
                dst = os.path.join(subcat_dir, f"{recipe}{ext}")
                if os.path.exists(src):
                    shutil.move(src, dst)
                    print(f"Moved Cook: {src} -> {dst}")

def move_md_files(base_dir, mapping):
    for subcat, md_files in mapping.items():
        subcat_dir = os.path.join(base_dir, subcat)
        os.makedirs(subcat_dir, exist_ok=True)
        for md_file in md_files:
            src = os.path.join(base_dir, md_file)
            dst = os.path.join(subcat_dir, md_file)
            if os.path.exists(src):
                shutil.move(src, dst)
                print(f"Moved Doc: {src} -> {dst}")
            else:
                print(f"Warning: Could not find {src}")

if __name__ == "__main__":
    # Move Cook files
    move_cook_files("cook/sides", sides_mapping)
    move_cook_files("cook/sauces-and-dressings", sauces_mapping)
    
    # Move special folders
    if os.path.exists("cook/sauces-and-dressings/5-mother-sauces"):
        shutil.move("cook/sauces-and-dressings/5-mother-sauces", "cook/sauces-and-dressings/mother-sauces")
    if os.path.exists("docs/sauces-and-dressings/5-mother-sauces"):
        shutil.move("docs/sauces-and-dressings/5-mother-sauces", "docs/sauces-and-dressings/mother-sauces")
    
    # Move pesto
    if os.path.exists("cook/sauces-and-dressings/pesto"):
        # We'll put pesto under gravy-and-savory-sauces or keep it separate? 
        # The spec said "gravy-and-savory-sauces". Let's put it there.
        os.makedirs("cook/sauces-and-dressings/gravy-and-savory-sauces", exist_ok=True)
        shutil.move("cook/sauces-and-dressings/pesto", "cook/sauces-and-dressings/gravy-and-savory-sauces/pesto")
    if os.path.exists("docs/sauces-and-dressings/pesto"):
        os.makedirs("docs/sauces-and-dressings/gravy-and-savory-sauces", exist_ok=True)
        shutil.move("docs/sauces-and-dressings/pesto", "docs/sauces-and-dressings/gravy-and-savory-sauces/pesto")

    # Move Docs
    move_md_files("docs/sides", sides_md)
    move_md_files("docs/sauces-and-dressings", sauces_md)
