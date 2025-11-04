"""
The Simple Kitchen - pandas-backed Tkinter recipe book

Replaces MySQL with local pandas CSV storage. Single-file app.

Features (same as requested):
- Main window with background image and a large styled button (exact UI specs preserved).
- Category chooser and category menu pages for VEGETARIAN, EGG-ETARIAN, NONVEGETARIAN.
- Recipes persisted in local CSV files: recipes.csv, recipe_images.csv, step_images.csv.
- Each recipe can have multiple recipe-images, per-step images, and an optional video file. Media files are copied into `media/` for persistence.
- Search bar, add recipe form, view details, delete user-added recipes (default recipes are protected).

SETUP
1) Install dependencies:
   pip install pandas pillow

2) Edit the IMAGE_PATH_* variables below to point to images on your computer. Prefer PNG for compatibility.

3) Run:
   python simple_kitchen_pandas.py

The script will create a `media/` folder and CSV files next to the script if they don't exist.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import os
import shutil
import uuid
from PIL import Image, ImageTk

# ---------------------- USER CONFIG ----------------------
IMAGE_PATH_MAIN_BG = r"path/to/your/main_background.png"
IMAGE_PATH_CAT_BG = r"path/to/your/category_background.png"
IMAGE_PATH_ICON = r"path/to/your/icon.png"
MEDIA_FOLDER = "media"
RECIPES_CSV = "recipes.csv"
RECIPE_IMAGES_CSV = "recipe_images.csv"
STEP_IMAGES_CSV = "step_images.csv"
# --------------------------------------------------------

DEFAULT_RECIPES = [{"id":1,"name":"Pani Puri","category": "VEGETARIAN",
    "ingredients":"4 servings:\nFOR PURI:\n1 cup semolina (sooji)\n2 tbsp all-purpose flour\nSalt to taste\nWater as needed\nOil for frying\n\nFOR PANI:\n1 cup mint leaves\n1/2 cup coriander leaves\n1 green chilli\n1-inch ginger\n1 tbsp tamarind pulp\n1 tsp cumin powder\nSalt to taste\n4 cups cold water\n\nFOR FILLING:\n2 boiled potatoes, mashed\n1/2 cup boiled chickpeas\nChaat masala, to taste",
    "steps":"•Mix semolina, flour, salt, and water to form a stiff dough. Rest 20 minutes.\n•Roll small puris and fry till crisp and puffed.\n•Blend mint, coriander, chilli, ginger, tamarind, cumin, and salt with water to make spiced pani.\n•Mix potatoes, chickpeas, and chaat masala for filling.\n•Crack puris, fill with stuffing, and pour pani before serving.",
    "video_path":"",
    "is_default":1},

    {"id":2,"name":"Channa Masala","category": "VEGETARIAN",
    "ingredients":"4 servings:\n1 cup chickpeas (soaked overnight)\n2 onions, chopped\n2 tomatoes, chopped\n1 tbsp ginger-garlic paste\n1 tsp cumin\n1 tsp coriander powder\n1/2 tsp turmeric\n1 tsp garam masala\n1/2 tsp chilli powder\n2 tbsp oil\nSalt to taste\nFresh coriander for garnish",
    "steps":"•Pressure cook soaked chickpeas until soft.\n•Heat oil in a pan, add cumin and sauté onions till golden.\n•Add ginger-garlic paste and cook for a minute.\n•Add tomatoes and all spices, cook till oil separates.\n•Add cooked chickpeas and simmer for 10 minutes.\n•Garnish with coriander and serve with rice or roti.",
    "video_path":"",
    "is_default":1},

    {"id":3,"name":"Bisi Bele Bath","category": "VEGETARIAN",
    "ingredients":"4 servings:\n1 cup rice\n1/2 cup toor dal\n1/2 cup mixed vegetables\n2 tbsp bisi bele bath powder\nTamarind pulp (small lemon size)\n2 tbsp ghee\nSalt to taste\nCurry leaves, mustard seeds, cashews for tempering",
    "steps":"•Cook rice and dal separately until soft.\n•Boil vegetables with tamarind pulp and salt.\n•Add cooked rice and dal, mix well.\n•Stir in bisi bele bath powder and simmer for 5 minutes.\n•In a small pan, heat ghee and add mustard seeds, curry leaves, and cashews.\n•Pour tempering over the rice mixture and serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":4,"name":"Papdi Chaat","category": "VEGETARIAN",
    "ingredients":"4 servings:\n12 papdis (crispy wafers)\n1/2 cup boiled potatoes, cubed\n1/2 cup boiled chickpeas\n1/2 cup yogurt, whisked\n2 tbsp tamarind chutney\n2 tbsp green chutney\nChaat masala, red chilli powder, and salt to taste\nCoriander leaves for garnish",
    "steps":"•Arrange papdis on a plate.\n•Top each with potatoes and chickpeas.\n•Drizzle yogurt, green chutney, and tamarind chutney.\n•Sprinkle chaat masala, chilli powder, and salt.\n•Garnish with coriander leaves and serve immediately.",
    "video_path":"",
    "is_default":1},

    {"id":5,"name":"Masala Dosa","category": "VEGETARIAN",
    "ingredients":"4 servings:\n2 cups dosa batter\n2 boiled potatoes, mashed\n1 onion, sliced\n1 green chilli, chopped\n1/2 tsp mustard seeds\n1/4 tsp turmeric\nSalt to taste\nOil for cooking",
    "steps":"•Heat oil in a pan and add mustard seeds.\n•Add onions, green chilli, turmeric, and sauté till soft.\n•Add mashed potatoes and salt; mix well.\n•Spread dosa batter on a hot tawa.\n•Drizzle oil around edges, cook till crisp.\n•Place filling in the center, fold, and serve hot with chutney and sambar.",
    "video_path":"",
    "is_default":1},

    {"id":6,"name":"Dal Makhni","category": "VEGETARIAN",
    "ingredients":"4 servings:\n1 cup whole black lentils (urad dal)\n1/4 cup kidney beans (rajma)\n2 onions, chopped\n2 tomatoes, pureed\n1 tbsp ginger-garlic paste\n1 tsp cumin\n1/2 tsp garam masala\n1/2 tsp chilli powder\n2 tbsp butter\n1/4 cup cream\nSalt to taste",
    "steps":"•Soak dal and rajma overnight, pressure cook until soft.\n•In a pan, heat butter and sauté cumin, onions, and ginger-garlic paste.\n•Add tomato puree, spices, and cook until oil separates.\n•Add cooked lentils, mash slightly, and simmer for 30 minutes.\n•Stir in cream, garnish with butter, and serve.",
    "video_path":"",
    "is_default":1},

    {"id":7,"name":"Pav Bhaji","category": "VEGETARIAN",
    "ingredients":"4 servings:\n2 tbsp butter\n1 onion, chopped\n1 tomato, chopped\n1/2 cup boiled peas\n2 boiled potatoes, mashed\n1/2 cup capsicum, chopped\n1 tsp pav bhaji masala\n1/2 tsp chilli powder\nSalt to taste\nPav buns\nLemon wedges and coriander for garnish",
    "steps":"•Heat butter in a pan, sauté onion till translucent.\n•Add tomato and cook till soft.\n•Add capsicum, peas, and mashed potatoes.\n•Add pav bhaji masala, chilli powder, and salt.\n•Mash with a masher and simmer for 5 minutes.\n•Toast pav buns with butter.\n•Serve bhaji hot with buns, lemon, and coriander.",
    "video_path":"",
    "is_default":1},

    {"id":8,"name":"Paneer Butter Masala","category": "VEGETARIAN",
    "ingredients":"4 servings:\n200g paneer, cubed\n2 onions, chopped\n2 tomatoes, pureed\n1 tbsp ginger-garlic paste\n1/2 tsp garam masala\n1/2 tsp chilli powder\n1/4 cup cream\n1 tbsp butter\n1 tbsp oil\nSalt to taste\n1 tsp kasuri methi",
    "steps":"•Heat butter and oil in a pan.\n•Sauté onions until golden, add ginger-garlic paste.\n•Add tomato puree and cook till oil separates.\n•Stir in chilli powder, garam masala, and salt.\n•Add paneer cubes and simmer 5 minutes.\n•Add cream and kasuri methi, mix gently.\n•Serve hot with naan or rice.",
    "video_path":"",
    "is_default":1},

    {"id":9,"name":"Tomato Chutney","category": "VEGETARIAN",
    "ingredients":"1 cup:\n3 ripe tomatoes, chopped\n2 dried red chillies\n1 tsp mustard seeds\n2 garlic cloves\n1 tbsp oil\nSalt to taste\nFew curry leaves",
    "steps":"•Heat oil in a pan, add mustard seeds and curry leaves.\n•Add chillies, garlic, and tomatoes.\n•Cook until tomatoes turn mushy.\n•Cool and blend into a smooth paste.\n•Serve with idli, dosa, or vada.",
    "video_path":"",
    "is_default":1},

    {"id":10,"name":"Veg Hakka Noodles","category": "VEGETARIAN",
    "ingredients":"2 servings:\n150g noodles\n1 tbsp oil\n1 clove garlic, minced\n1 onion, sliced\n1/2 cup carrot, capsicum, and cabbage, julienned\n1 tbsp soy sauce\n1 tsp vinegar\n1/2 tsp pepper\nSalt to taste\nSpring onions for garnish",
    "steps":"•Boil noodles, drain, and toss with oil.\n•Heat oil in a wok, sauté garlic and onion.\n•Add vegetables and stir-fry on high flame.\n•Add soy sauce, vinegar, salt, and pepper.\n•Add noodles and toss well.\n•Garnish with spring onions and serve.",
    "video_path":"",
    "is_default":1},

    {"id":11,"name":"Malai Kofta","category": "VEGETARIAN",
    "ingredients":"4 servings:\nFOR KOFTA:\n2 boiled potatoes\n1/2 cup grated paneer\n2 tbsp corn flour\nSalt to taste\nOil for frying\n\nFOR GRAVY:\n2 onions, chopped\n2 tomatoes, pureed\n1 tbsp ginger-garlic paste\n1/2 tsp garam masala\n1/4 cup cream\n1 tbsp butter\n1 tsp chilli powder\nSalt to taste",
    "steps":"•Mix potatoes, paneer, corn flour, and salt; shape into balls and deep fry till golden.\n•Heat butter, sauté onions and ginger-garlic paste.\n•Add tomato puree, spices, and salt; cook till oil separates.\n•Add cream and mix well.\n•Add koftas just before serving and garnish with cream.",
    "video_path":"",
    "is_default":1},

    {"id":12,"name":"Khichdi","category": "VEGETARIAN",
    "ingredients":"4 servings:\n1/2 cup rice\n1/4 cup moong dal\n1 onion, chopped\n1 tomato, chopped\n1/2 tsp cumin\n1/4 tsp turmeric\nSalt to taste\n1 tbsp ghee\n3 cups water",
    "steps":"•Wash rice and dal, soak for 15 minutes.\n•Heat ghee in a pressure cooker, add cumin, onions, and sauté.\n•Add tomatoes, turmeric, and salt.\n•Add rice, dal, and water.\n•Pressure cook for 3 whistles.\n•Serve with ghee and papad.",
    "video_path":"",
    "is_default":1},

    {"id":13,"name":"Veg Fried Rice","category": "VEGETARIAN",
    "ingredients":"2 servings:\n2 cups cooked rice\n1 tbsp oil\n1 garlic clove, minced\n1/2 cup chopped vegetables (carrot, beans, peas, capsicum)\n1 tbsp soy sauce\n1/2 tsp pepper\nSalt to taste\nSpring onions for garnish",
    "steps":"•Heat oil in a wok and sauté garlic.\n•Add vegetables and stir-fry 2–3 minutes.\n•Add soy sauce, salt, and pepper.\n•Add cooked rice and toss on high flame.\n•Garnish with spring onions and serve.",
    "video_path":"",
    "is_default":1},

    {"id":14,"name":"Aloo Chaat","category": "VEGETARIAN",
    "ingredients":"2 servings:\n2 boiled potatoes, cubed\n1 tbsp oil\n1/2 tsp chaat masala\n1/4 tsp chilli powder\nSalt to taste\n1 tbsp lemon juice\nChopped coriander for garnish",
    "steps":"•Heat oil in a pan and shallow-fry potatoes until crisp.\n•Add chaat masala, chilli powder, and salt.\n•Mix well and drizzle with lemon juice.\n•Garnish with coriander and serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":15,"name":"Pulihora","category": "VEGETARIAN",
    "ingredients":"4 servings:\n2 cups cooked rice\n2 tbsp tamarind pulp\n1 tbsp sesame oil\n1/2 tsp mustard seeds\n1 dried red chilli\nFew curry leaves\n1 tbsp peanuts\nSalt to taste",
    "steps":"•Heat oil in a pan, add mustard seeds, red chilli, curry leaves, and peanuts.\n•Add tamarind pulp and cook until thickened.\n•Add salt and mix with cooked rice.\n•Toss well and serve.",
    "video_path":"",
    "is_default":1},

    {"id":16,"name":"Mirchi Bajjii","category": "VEGETARIAN",
    "ingredients":"4 servings:\n6 large green chillies\n1 cup gram flour\n1/4 tsp turmeric\n1/2 tsp chilli powder\nSalt to taste\nWater as needed\nOil for frying",
    "steps":"•Slit chillies and remove seeds if desired.\n•Mix gram flour, spices, and water into a smooth batter.\n•Dip each chilli into the batter and deep fry until golden.\n•Serve with chutney.",
    "video_path":"",
    "is_default":1},

    {"id":17,"name":"Pesarattu","category": "VEGETARIAN",
    "ingredients":"4 servings:\n1 cup green gram (moong dal)\n1-inch ginger\n2 green chillies\nSalt to taste\nOil for cooking",
    "steps":"•Soak green gram overnight and grind with ginger, chillies, and salt into a smooth batter.\n•Pour batter on a hot tawa and spread thinly.\n•Drizzle oil around edges and cook till crisp.\n•Fold and serve with upma or chutney.",
    "video_path":"",
    "is_default":1},

    {"id":18,"name":"Khandvi","category": "VEGETARIAN",
    "ingredients":"4 servings:\n1 cup gram flour\n1 cup yogurt\n2 cups water\n1/2 tsp turmeric\nSalt to taste\n1 tsp mustard seeds\nCurry leaves\nGrated coconut for garnish",
    "steps":"•Whisk gram flour, yogurt, water, turmeric, and salt until smooth.\n•Cook on low flame, stirring till thick.\n•Spread thin layer on a greased surface and roll when cool.\n•Heat oil, add mustard seeds and curry leaves; pour over rolls.\n•Garnish with coconut.",
    "video_path":"",
    "is_default":1},

    {"id":19,"name":"Garlic Cheese Toast","category": "VEGETARIAN",
    "ingredients":"2 servings:\n4 bread slices\n2 tbsp butter\n2 garlic cloves, minced\n1/2 cup grated cheese\n1 tsp parsley",
    "steps":"•Mix butter and garlic, spread on bread slices.\n•Sprinkle cheese and parsley.\n•Toast in oven or pan till golden and cheese melts.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":20,"name":"Veg Momos","category": "VEGETARIAN",
    "ingredients":"4 servings:\n1 cup all-purpose flour\n1/2 cup chopped vegetables (cabbage, carrot, capsicum)\n1 tsp soy sauce\n1 tsp oil\nSalt to taste\nWater for dough",
    "steps":"•Knead flour and water into soft dough.\n•Sauté vegetables with soy sauce and salt.\n•Roll small dough circles, fill with mixture, and shape momos.\n•Steam for 10 minutes and serve with chutney.",
    "video_path":"",
    "is_default":1},

    {"id":21,"name":"Paneer 65","category": "VEGETARIAN",
    "ingredients":"4 servings:\n200g paneer, cubed\n2 tbsp corn flour\n1 tbsp rice flour\n1 tsp chilli powder\n1/4 tsp turmeric\nSalt to taste\nOil for frying\nCurry leaves and green chillies for garnish",
    "steps":"•Mix flours, spices, and salt with water to make batter.\n•Coat paneer cubes and deep fry till crisp.\n•Toss with fried curry leaves and chillies.\n•Serve hot as snack.",
    "video_path":"",
    "is_default":1},

    {"id":22,"name":"Honey Chilli Potato","category": "VEGETARIAN",
    "ingredients":"2 servings:\n2 potatoes, cut into fingers\n2 tbsp corn flour\n1 tbsp soy sauce\n1 tbsp tomato ketchup\n1 tbsp honey\n1/2 tsp chilli flakes\n1 tbsp oil\nSesame seeds for garnish",
    "steps":"•Coat potato fingers with corn flour and deep fry till golden.\n•In a wok, heat oil, add soy sauce, ketchup, honey, and chilli flakes.\n•Add fried potatoes and toss well.\n•Garnish with sesame seeds and serve.",
    "video_path":"",
    "is_default":1},

    {"id":23,"name":"Veg Taco Skillet","category": "VEGETARIAN",
    "ingredients":"2 servings:\n1 tbsp oil\n1 onion, chopped\n1 bell pepper, chopped\n1 cup cooked beans\n1/2 cup corn\n1 tbsp taco seasoning\n1/2 cup cheese\nTortilla chips for serving",
    "steps":"•Heat oil in a pan and sauté onions and bell pepper.\n•Add beans, corn, and taco seasoning.\n•Simmer for 5 minutes.\n•Top with cheese and cover till melted.\n•Serve with tortilla chips.",
    "video_path":"",
    "is_default":1},

    {"id":24,"name":"Creamy Tomato Spaghetti","category": "VEGETARIAN",
    "ingredients":"2 servings:\n150g spaghetti\n1 tbsp olive oil\n2 garlic cloves\n2 tomatoes, pureed\n1/4 cup cream\nSalt and pepper to taste\nBasil leaves for garnish",
    "steps":"•Cook spaghetti as per packet instructions.\n•Heat oil, sauté garlic, and add tomato puree.\n•Simmer 5 minutes, add cream, salt, and pepper.\n•Toss in spaghetti and garnish with basil.",
    "video_path":"",
    "is_default":1},

    {"id":25,"name":"Mushroom and Spinach Pasta","category": "VEGETARIAN",
    "ingredients":"2 servings:\n150g pasta\n1 tbsp olive oil\n1 cup mushrooms, sliced\n1 cup spinach\n1/2 cup cream\nSalt and pepper to taste\nGrated cheese for garnish",
    "steps":"•Cook pasta until al dente.\n•Heat oil and sauté mushrooms till brown.\n•Add spinach and cook till wilted.\n•Add cream, salt, and pepper.\n•Mix in pasta, toss well, and garnish with cheese.",
    "video_path":"",
    "is_default":1},

    {"id":26,"name":"Vegetarian Miso Noodle Soup with Mushrooms","category": "VEGETARIAN",
    "ingredients":"2 servings:\n4 cups vegetable broth\n1 tbsp miso paste\n1 cup mushrooms\n100g noodles\n1 tbsp soy sauce\n1 tsp sesame oil\nSpring onions for garnish",
    "steps":"•Heat broth in a pot, add miso paste and stir until dissolved.\n•Add mushrooms and soy sauce, simmer 5 minutes.\n•Add noodles and cook till soft.\n•Drizzle sesame oil and garnish with spring onions.",
    "video_path":"",
    "is_default":1},

    {"id":27,"name":"Mediterranean Lentil Salad with Feta","category": "VEGETARIAN",
    "ingredients":"2 servings:\n1 cup cooked lentils\n1/2 cup cherry tomatoes\n1/4 cup cucumber, diced\n1/4 cup red onion, chopped\n2 tbsp olive oil\n1 tbsp lemon juice\n1/4 cup feta cheese\nSalt and pepper to taste",
    "steps":"•Combine lentils, tomatoes, cucumber, and onion in a bowl.\n•Whisk olive oil, lemon juice, salt, and pepper.\n•Toss dressing with salad and top with feta.",
    "video_path":"",
    "is_default":1},

    {"id":28,"name":"Black Bean Burritos","category": "VEGETARIAN",
    "ingredients":"2 servings:\n4 tortillas\n1 cup cooked black beans\n1/2 cup cooked rice\n1/2 cup corn\n1/2 cup salsa\n1/4 cup cheese\nLettuce and sour cream to serve",
    "steps":"•Warm tortillas slightly.\n•Mix beans, rice, corn, salsa, and cheese.\n•Place mixture in center of tortilla, roll tightly.\n•Serve with lettuce and sour cream.",
    "video_path":"",
    "is_default":1},

    {"id":29,"name":"Egg Curry","category":"EGG-ETARIAN",
    "ingredients":"4 servings:\n6 boiled eggs\n2 onions, finely chopped\n2 tomatoes, pureed\n1 tbsp ginger-garlic paste\n1 tsp cumin seeds\n1/2 tsp turmeric\n1 tsp coriander powder\n1/2 tsp chilli powder\n1/2 tsp garam masala\n2 tbsp oil\nSalt to taste\nFresh coriander for garnish",
    "steps":"•Heat oil in a pan and add cumin seeds.\n•Add onions and sauté until golden brown.\n•Stir in ginger-garlic paste and cook for a minute.\n•Add tomato puree, turmeric, coriander powder, and chilli powder.\n•Cook until oil separates.\n•Add 1/2 cup water and bring to a boil.\n•Add boiled eggs (halved) and simmer for 5 minutes.\n•Sprinkle garam masala, garnish with coriander, and serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":30,"name":"Vegetable Egg Fried Rice","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 cups cooked rice\n2 eggs, lightly beaten\n1 tbsp oil\n1 garlic clove, minced\n1/2 cup mixed vegetables (carrot, beans, peas, corn)\n1 tbsp soy sauce\n1 tsp vinegar\nSalt and pepper to taste\nSpring onions for garnish",
    "steps":"•Heat oil in a wok and add garlic.\n•Add beaten eggs, scramble lightly, and cook until soft.\n•Add vegetables and stir-fry 2–3 minutes.\n•Add rice, soy sauce, vinegar, salt, and pepper.\n•Toss everything on high heat.\n•Garnish with spring onions and serve.",
    "video_path":"",
    "is_default":1},

    {"id":31,"name":"Spinach and Mushroom Omelette","category":"EGG-ETARIAN",
    "ingredients":"1 serving:\n2 eggs\n1/2 cup spinach, chopped\n1/4 cup mushrooms, sliced\n1 tbsp milk\n1 tbsp butter\nSalt and pepper to taste\nGrated cheese (optional)",
    "steps":"•Beat eggs with milk, salt, and pepper.\n•Heat butter in a non-stick pan and sauté mushrooms and spinach for 2 minutes.\n•Pour egg mixture and cook on medium heat.\n•Add cheese if desired.\n•Fold and serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":32,"name":"Egg Bhurji","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n3 eggs\n1 onion, chopped\n1 tomato, chopped\n1 green chilli, chopped\n1/4 tsp turmeric\n1/2 tsp chilli powder\nSalt to taste\n1 tbsp oil\nCoriander leaves for garnish",
    "steps":"•Heat oil in a pan and add onions and green chilli.\n•Sauté till onions soften.\n•Add tomatoes, turmeric, and chilli powder.\n•Cook till tomatoes turn mushy.\n•Add beaten eggs and cook while stirring continuously.\n•Garnish with coriander and serve with bread or roti.",
    "video_path":"",
    "is_default":1},

    {"id":33,"name":"Egg Sandwich","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n4 slices of bread\n2 boiled eggs, chopped\n2 tbsp mayonnaise\n1 tsp mustard\nSalt and pepper to taste\nButter for toasting",
    "steps":"•Mix chopped eggs, mayonnaise, mustard, salt, and pepper in a bowl.\n•Spread mixture between two bread slices.\n•Butter outer sides and toast on a pan until golden brown.\n•Serve warm or cold.",
    "video_path":"",
    "is_default":1},

    {"id":34,"name":"Shakshuka","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 tbsp olive oil\n1 onion, chopped\n2 cloves garlic, minced\n1 red bell pepper, diced\n4 tomatoes, chopped (or 1 can crushed tomatoes)\n1 tsp cumin\n1/2 tsp paprika\n1/2 tsp chilli powder\n4 eggs\nSalt and pepper to taste\nFresh parsley for garnish",
    "steps":"•Heat olive oil in a pan and sauté onion and garlic until fragrant.\n•Add bell pepper and cook until soft.\n•Add tomatoes and spices, simmer until thickened.\n•Make small wells and crack eggs into them.\n•Cover and cook until eggs are set to your liking.\n•Garnish with parsley and serve with bread.",
    "video_path":"",
    "is_default":1},

    {"id":35,"name":"Egg Dosa","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n1 cup dosa batter\n2 eggs\n1 onion, finely chopped\n1 green chilli, chopped\nSalt and pepper to taste\nOil for cooking",
    "steps":"•Heat tawa and spread dosa batter thinly.\n•Break one egg on top, spread evenly, and sprinkle onion, chilli, salt, and pepper.\n•Drizzle oil around edges and cook until golden.\n•Fold and serve with chutney or sambar.",
    "video_path":"",
    "is_default":1},

    {"id":36,"name":"Egg Paratha","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 cups wheat flour\n2 eggs\n1 onion, chopped\n1 green chilli, chopped\nSalt and pepper to taste\nOil or ghee for roasting",
    "steps":"•Knead flour with water to form dough, rest for 15 minutes.\n•Roll into a circle and cook lightly on a tawa.\n•Crack an egg on top, spread with spoon, sprinkle onion, chilli, salt, and pepper.\n•Flip and cook both sides with oil until golden.\n•Serve hot with yogurt or pickle.",
    "video_path":"",
    "is_default":1},

    {"id":37,"name":"Egg Fried Noodles","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n150g noodles\n2 eggs\n1 tbsp oil\n1 garlic clove, minced\n1/2 cup mixed vegetables (capsicum, carrot, beans)\n1 tbsp soy sauce\n1/2 tsp pepper\nSalt to taste\nSpring onions for garnish",
    "steps":"•Cook noodles and drain.\n•Heat oil, add garlic and vegetables, stir-fry for 2 minutes.\n•Push to one side, scramble eggs on the other.\n•Add noodles, soy sauce, salt, and pepper.\n•Toss well, garnish with spring onions.",
    "video_path":"",
    "is_default":1},

    {"id":38,"name":"Egg Biryani","category":"EGG-ETARIAN",
    "ingredients":"4 servings:\n4 boiled eggs\n1 1/2 cups basmati rice\n2 onions, sliced\n1 tomato, chopped\n1 tbsp ginger-garlic paste\n1 tsp garam masala\n1/2 tsp turmeric\n1/2 tsp chilli powder\n2 tbsp oil\n1 tbsp ghee\nFresh coriander and mint\nSalt to taste",
    "steps":"•Cook rice until 90% done, drain and keep aside.\n•Heat oil, sauté onions until golden.\n•Add ginger-garlic paste, tomato, and spices.\n•Add boiled eggs and mix gently.\n•Layer rice over masala, sprinkle mint and coriander.\n•Cover and steam for 10 minutes.\n•Serve hot with raita.",
    "video_path":"",
    "is_default":1},

    {"id":39,"name":"Spanish Omelette","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n3 eggs\n1 potato, thinly sliced\n1 onion, sliced\n2 tbsp olive oil\nSalt and pepper to taste",
    "steps":"•Heat olive oil in a pan and cook potato slices till soft.\n•Add onions and cook until translucent.\n•Beat eggs with salt and pepper, pour over potatoes.\n•Cook on low flame until set.\n•Flip carefully and cook the other side.\n•Serve warm.",
    "video_path":"",
    "is_default":1},

    {"id":40,"name":"Egg Pasta Carbonara (Vegetarian)","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n150g spaghetti\n2 eggs\n1/4 cup grated parmesan or vegetarian cheese\n1 tbsp olive oil\n2 cloves garlic, minced\nSalt and pepper to taste\nParsley for garnish",
    "steps":"•Cook spaghetti al dente, reserve 1/4 cup pasta water.\n•Beat eggs with cheese, salt, and pepper.\n•Heat oil, sauté garlic, add cooked pasta.\n•Turn off heat, quickly stir in egg mixture with a splash of hot pasta water.\n•Toss well till creamy.\n•Garnish with parsley.",
    "video_path":"",
    "is_default":1},

    {"id":41,"name":"Egg Curry Rice Bowl","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 boiled eggs\n1 cup cooked rice\n1/2 cup curry sauce (any mild curry)\n1 tbsp oil\nSalt to taste\nCoriander for garnish",
    "instrustepsctions":"•Heat curry sauce in a pan.\n•Add boiled eggs and simmer for 5 minutes.\n•Serve hot over steamed rice.\n•Garnish with coriander.",
    "video_path":"",
    "is_default":1},

    {"id":42,"name":"Masala Egg Toast","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n4 slices bread\n2 eggs\n1 small onion, chopped\n1 green chilli, chopped\n1 tbsp milk\nSalt and pepper to taste\nButter or oil for toasting",
    "steps":"•Beat eggs with onion, chilli, milk, salt, and pepper.\n•Heat butter on a pan, dip each bread slice in the mixture.\n•Cook both sides till golden.\n•Serve hot with ketchup or chutney.",
    "video_path":"",
    "is_default":1},

    {"id":43,"name":"Egg Manchurian","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n4 boiled eggs (halved)\n1/4 cup corn flour\n2 tbsp soy sauce\n1 tbsp tomato ketchup\n1 tsp vinegar\n1 onion, chopped\n1 capsicum, chopped\n1 tbsp oil\nSalt and pepper to taste",
    "steps":"•Coat egg halves in corn flour, shallow fry till golden.\n•In the same pan, sauté onion and capsicum.\n•Add sauces, vinegar, and pepper.\n•Add eggs, toss gently.\n•Serve as snack or with fried rice.",
    "video_path":"",
    "is_default":1},

    {"id":44,"name":"Vegetable Egg Wrap","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 eggs\n2 chapatis or tortillas\n1/2 cup grated carrot\n1/4 cup sliced cucumber\n1/4 cup lettuce\n1 tbsp mayonnaise or yogurt sauce\nSalt and pepper to taste",
    "steps":"•Beat eggs and cook into thin omelettes.\n•Place omelette over chapati.\n•Add vegetables and sauce, sprinkle salt and pepper.\n•Roll tightly and serve.",
    "video_path":"",
    "is_default":1},

    {"id":45,"name":"Egg Pakora","category":"EGG-ETARIAN",
    "ingredients":"4 servings:\n4 boiled eggs, halved\n1 cup gram flour\n1/2 tsp turmeric\n1/2 tsp chilli powder\nSalt to taste\nWater as needed\nOil for frying",
    "steps":"•Mix gram flour, spices, salt, and water into thick batter.\n•Dip egg halves into batter and deep fry till golden.\n•Serve hot with chutney.",
    "video_path":"",
    "is_default":1},

    {"id":46,"name":"Egg Kathi Roll","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 parathas\n2 eggs\n1 onion, sliced\n1/4 cup capsicum\n1 tbsp tomato sauce\nSalt and pepper to taste\nOil for cooking",
    "steps":"•Cook parathas and keep aside.\n•Beat eggs with salt and pepper.\n•Pour egg on tawa, place paratha on top to stick.\n•Flip, cook other side.\n•Add sautéed onion, capsicum, and sauce.\n•Roll and serve.",
    "video_path":"",
    "is_default":1},

    {"id":47,"name":"Baked Egg Muffins","category":"EGG-ETARIAN",
    "ingredients":"6 muffins:\n4 eggs\n1/2 cup spinach, chopped\n1/4 cup cheese\n1/4 cup diced bell pepper\nSalt and pepper to taste",
    "steps":"•Preheat oven to 180°C.\n•Beat eggs with salt and pepper.\n•Mix in spinach, cheese, and bell pepper.\n•Pour into greased muffin cups.\n•Bake 15–20 minutes till set.\n•Cool slightly and serve.",
    "video_path":"",
    "is_default":1},

    {"id":48,"name":"Egg Rice","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 cups cooked rice\n2 eggs\n1 onion, chopped\n1 green chilli, chopped\n1/4 tsp turmeric\n1/2 tsp pepper\n1 tbsp oil\nSalt to taste",
    "steps":"•Heat oil in a pan, sauté onions and chilli.\n•Add turmeric and salt.\n•Push aside, scramble eggs.\n•Add rice, mix well, sprinkle pepper.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":49,"name":"Egg Masala Sandwich","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n4 slices bread\n2 boiled eggs\n1/2 onion, chopped\n1/2 tomato, chopped\n1/2 tsp garam masala\nSalt to taste\nButter for toasting",
    "steps":"•Mash boiled eggs, mix with onion, tomato, spices, and salt.\n•Spread on bread slices.\n•Butter outer sides and toast till golden.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":50,"name":"Egg Salad Bowl","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 boiled eggs, sliced\n1 cup lettuce\n1/4 cup cherry tomatoes\n1/4 cucumber, sliced\n1 tbsp olive oil\n1 tbsp lemon juice\nSalt and pepper to taste",
    "steps":"•Arrange lettuce, tomato, and cucumber in a bowl.\n•Add sliced eggs on top.\n•Drizzle olive oil and lemon juice.\n•Season with salt and pepper.\n•Serve fresh.",
    "video_path":"",
    "is_default":1},

    {"id":51,"name":"Egg Curry with Coconut Milk","category":"EGG-ETARIAN",
    "ingredients":"4 servings:\n6 boiled eggs\n1 onion, chopped\n2 tomatoes, pureed\n1 tbsp ginger-garlic paste\n1/2 cup coconut milk\n1 tsp curry powder\n1/2 tsp turmeric\n1 tbsp oil\nSalt to taste",
    "steps":"•Heat oil, sauté onions and ginger-garlic paste.\n•Add tomato puree and spices, cook until oil separates.\n•Add coconut milk and simmer.\n•Add eggs and cook 5 minutes.\n•Serve with rice or appam.",
    "video_path":"",
    "is_default":1},

    {"id":52,"name":"Egg Bhuna Masala","category":"EGG-ETARIAN",
    "ingredients":"4 servings:\n4 boiled eggs\n2 onions, sliced\n2 tomatoes, pureed\n1 tbsp ginger-garlic paste\n1 tsp garam masala\n1/2 tsp chilli powder\nSalt to taste\n2 tbsp oil",
    "steps":"•Heat oil and sauté onions till golden.\n•Add ginger-garlic paste, tomato puree, and spices.\n•Cook till thick masala forms.\n•Add eggs, coat gently.\n•Serve hot with paratha.",
    "video_path":"",
    "is_default":1},

    {"id":53,"name":"Eggplant and Egg Stir-Fry","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n1 cup eggplant, diced\n2 eggs\n1 onion, sliced\n1 tbsp soy sauce\n1 tbsp oil\nSalt and pepper to taste",
    "steps":"•Heat oil in a pan and sauté onions and eggplant till soft.\n•Push aside and scramble eggs.\n•Add soy sauce, salt, and pepper.\n•Mix well and serve.",
    "video_path":"",
    "is_default":1},

    {"id":54,"name":"Egg Pulao","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n1 cup basmati rice\n2 boiled eggs\n1 onion, sliced\n1 tomato, chopped\n1 tsp cumin\n1/2 tsp garam masala\n1 tbsp ghee\nSalt to taste",
    "steps":"•Cook rice separately.\n•Heat ghee, add cumin, onion, and tomato.\n•Add spices and salt.\n•Add rice and mix.\n•Top with boiled eggs cut in halves and serve.",
    "video_path":"",
    "is_default":1},

    {"id":55,"name":"Cheese Omelette","category":"EGG-ETARIAN",
    "ingredients":"1 serving:\n2 eggs\n2 tbsp milk\n1/4 cup grated cheese\nSalt and pepper to taste\n1 tsp butter",
    "steps":"•Beat eggs with milk, salt, and pepper.\n•Heat butter in a pan and pour egg mixture.\n•Sprinkle cheese, fold and cook till set.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":56,"name":"Curried Egg Sandwich","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n4 slices bread\n2 boiled eggs, mashed\n1 tbsp mayonnaise\n1/2 tsp curry powder\nSalt and pepper to taste",
    "steps":"•Mix eggs with mayo, curry powder, salt, and pepper.\n•Spread between bread slices.\n•Serve fresh or toasted.",
    "video_path":"",
    "is_default":1},

    {"id":57,"name":"Vegetable Egg Pizza","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n1 pizza base\n2 eggs\n1/4 cup tomato sauce\n1/2 cup vegetables (bell pepper, onion, tomato)\n1/4 cup cheese\nSalt and oregano to taste",
    "steps":"•Spread sauce on pizza base.\n•Add vegetables and crack eggs on top.\n•Sprinkle cheese and seasoning.\n•Bake at 200°C for 10–12 minutes.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":58,"name":"Egg Idli","category":"EGG-ETARIAN",
    "ingredients":"4 servings:\n1 cup idli batter\n2 boiled eggs, chopped\n1 onion, chopped\n1 green chilli, chopped\nSalt to taste",
    "steps":"•Mix idli batter with onion, chilli, eggs, and salt.\n•Pour into greased idli moulds.\n•Steam 10–12 minutes.\n•Serve with chutney.",
    "video_path":"",
    "is_default":1},

    {"id":59,"name":"Eggplant Parmesan with Egg Coating","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n1 small eggplant, sliced\n1 egg, beaten\n1/4 cup breadcrumbs\n1/4 cup tomato sauce\n1/4 cup cheese\nSalt and pepper to taste",
    "steps":"•Dip eggplant slices in beaten egg, coat with breadcrumbs.\n•Pan-fry till golden.\n•Layer with tomato sauce and cheese.\n•Bake at 180°C for 10 minutes.\n•Serve warm.",
    "video_path":"",
    "is_default":1},

    {"id":60,"name":"Egg Paneer Bhurji","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 eggs\n100g paneer, crumbled\n1 onion, chopped\n1 tomato, chopped\n1/2 tsp turmeric\n1/2 tsp chilli powder\nSalt to taste\n1 tbsp oil",
    "steps":"•Heat oil, sauté onion and tomato.\n•Add spices, then paneer and eggs.\n•Stir continuously till eggs set.\n•Serve hot with roti.",
    "video_path":"",
    "is_default":1},

    {"id":61,"name":"Eggplant Stir-Fry with Scrambled Egg","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n1 cup chopped eggplant\n2 eggs\n1 onion, sliced\n1 tbsp soy sauce\n1 tbsp oil\nSalt and pepper to taste",
    "steps":"•Sauté onion and eggplant till tender.\n•Push aside, scramble eggs.\n•Add soy sauce, mix everything.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":62,"name":"Egg Poha","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n1 cup poha (flattened rice)\n2 eggs\n1 onion, chopped\n1 green chilli, chopped\n1/4 tsp turmeric\nSalt to taste\n1 tbsp oil",
    "steps":"•Rinse poha and drain.\n•Heat oil, sauté onions and chilli.\n•Add turmeric, salt, and eggs; scramble.\n•Add poha, mix well.\n•Serve with lemon.",
    "video_path":"",
    "is_default":1},

    {"id":63,"name":"Egg Spinach Sandwich","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n4 slices bread\n2 eggs\n1/2 cup spinach, chopped\n1 tbsp mayonnaise\nSalt and pepper to taste\nButter for toasting",
    "steps":"•Scramble eggs with spinach, salt, and pepper.\n•Spread mayo on bread, add filling.\n•Toast lightly with butter.\n•Serve warm.",
    "video_path":"",
    "is_default":1},

    {"id":64,"name":"Egg Tacos","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n4 small tortillas\n2 eggs\n1/4 cup chopped bell peppers\n1/4 cup onion\n1/4 cup cheese\nSalt and pepper to taste",
    "steps":"•Scramble eggs with onion and peppers.\n•Warm tortillas, fill with eggs and cheese.\n•Fold and serve.",
    "video_path":"",
    "is_default":1},

    {"id":65,"name":"Egg Fried Cauliflower Rice","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 cups grated cauliflower\n2 eggs\n1/2 cup mixed vegetables\n1 tbsp soy sauce\n1 tsp oil\nSalt and pepper to taste",
    "steps":"•Heat oil, add vegetables and cauliflower, stir-fry 5 minutes.\n•Push aside, scramble eggs.\n•Add soy sauce, salt, and pepper.\n•Mix well and serve.",
    "video_path":"",
    "is_default":1},

    {"id":66,"name":"Egg Veggie Pancakes","category":"EGG-ETARIAN",
    "ingredients":"4 small pancakes:\n2 eggs\n1/4 cup grated carrot\n1/4 cup chopped spinach\n2 tbsp flour\nSalt and pepper to taste\nOil for cooking",
    "steps":"•Whisk eggs, add veggies, flour, salt, and pepper.\n•Pour batter onto hot pan.\n•Cook both sides till golden.\n•Serve with ketchup.",
    "video_path":"",
    "is_default":1},

    {"id":67,"name":"Egg Ramen Bowl","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n100g ramen noodles\n2 eggs\n2 cups vegetable broth\n1 tbsp soy sauce\n1 tsp sesame oil\n1/2 cup mushrooms\nSpring onions for garnish",
    "steps":"•Cook noodles in broth with soy sauce and mushrooms.\n•Boil eggs separately, peel and halve.\n•Serve noodles in bowl with broth.\n•Top with eggs, drizzle sesame oil, and garnish.",
    "video_path":"",
    "is_default":1},

    {"id":68,"name":"Stuffed Bell Peppers with Egg","category":"EGG-ETARIAN",
    "ingredients":"2 servings:\n2 bell peppers, halved\n2 eggs\n1/4 cup onion, chopped\n1/4 cup spinach, chopped\nSalt and pepper to taste\n1 tbsp olive oil",
    "steps":"•Sauté onion and spinach lightly.\n•Place bell pepper halves on baking tray, add filling, crack egg on top.\n•Season with salt and pepper.\n•Bake at 180°C for 15 minutes.\n•Serve warm.",
    "video_path":"",
    "is_default":1},

    {"id":69,"name":"Butter Chicken","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g boneless chicken\n1 cup yogurt\n1 tbsp ginger garlic paste\n1 tsp chilli powder\n1/2 tsp turmeric\n1 tbsp lemon juice\n2 tbsp butter\n1 onion, chopped\n2 tomatoes, pureed\n1/2 cup cream\n1 tsp garam masala\nSalt to taste",
    "steps":"•Marinate chicken with yogurt, spices, lemon juice for 1 hour.\n•Cook chicken in pan until sealed.\n•In another pan, melt butter, add onion and tomato puree.\n•Add cream and garam masala.\n•Mix in cooked chicken and simmer for 10 minutes.\n•Serve with naan or rice.",
    "video_path":"",
    "is_default":1},

    {"id":70,"name":"Chicken Biryani","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g chicken\n2 cups basmati rice\n2 onions, sliced\n1 tomato, chopped\n1 tbsp ginger garlic paste\n1 tsp garam masala\n1/2 tsp turmeric\n2 tbsp ghee\n1/4 cup curd\nMint and coriander\nSalt to taste",
    "steps":"•Marinate chicken with curd and spices.\n•Fry onions till golden, add tomato and chicken.\n•Cook till tender.\n•Layer with parboiled rice, mint, coriander.\n•Cover and cook 15 minutes on low flame.\n•Serve hot with raita.",
    "video_path":"",
    "is_default":1},

    {"id":71,"name":"Fish Curry","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n400g fish pieces\n1 onion, chopped\n1 tomato, chopped\n1 tbsp ginger garlic paste\n1 cup coconut milk\n1 tsp turmeric\n1 tsp chilli powder\n1 tbsp oil\nSalt to taste",
    "steps":"•Marinate fish with salt and turmeric.\n•Sauté onion and ginger-garlic paste.\n•Add tomato and spices, cook till oil separates.\n•Pour coconut milk and simmer.\n•Add fish, cook gently for 10 minutes.\n•Serve with rice.",
    "video_path":"",
    "is_default":1},

    {"id":72,"name":"Chicken 65","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n400g boneless chicken\n1/2 cup curd\n1 tbsp ginger garlic paste\n1 tsp red chilli powder\n1/2 tsp turmeric\n2 tbsp cornflour\n1 tbsp rice flour\nOil for frying\nCurry leaves\nSalt to taste",
    "steps":"•Marinate chicken with all ingredients for 1 hour.\n•Deep fry till crisp.\n•Toss in fried curry leaves before serving.\n•Serve hot with lemon wedges.",
    "video_path":"",
    "is_default":1},

    {"id":73,"name":"Mutton Curry","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g mutton\n2 onions, sliced\n1 tomato, chopped\n1 tbsp ginger garlic paste\n1 tsp coriander powder\n1/2 tsp turmeric\n1 tsp garam masala\n1 cup water\nSalt and oil to taste",
    "steps":"•Pressure cook mutton with salt and turmeric for 3 whistles.\n•Sauté onions and paste till golden.\n•Add tomatoes, spices, and cooked mutton.\n•Simmer until gravy thickens.\n•Serve hot with roti or rice.",
    "video_path":"",
    "is_default":1},

    {"id":74,"name":"Prawn Masala","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n300g prawns, cleaned\n1 onion, chopped\n1 tomato, pureed\n1 tbsp ginger garlic paste\n1 tsp cumin\n1/2 tsp turmeric\n1/2 tsp chilli powder\n2 tbsp oil\nSalt to taste",
    "steps":"•Marinate prawns with turmeric and salt.\n•Sauté onion and paste till brown.\n•Add tomato puree and spices.\n•Add prawns, cook for 5–7 minutes.\n•Serve with lemon and rice.",
    "video_path":"",
    "is_default":1},

    {"id":75,"name":"Egg Chicken Curry","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n300g chicken\n2 boiled eggs\n1 onion, chopped\n1 tomato, chopped\n1 tbsp ginger garlic paste\n1 tsp curry powder\nSalt and oil to taste",
    "steps":"•Cook chicken with spices till soft.\n•Add boiled eggs and simmer in curry sauce.\n•Serve warm with chapati or rice.",
    "video_path":"",
    "is_default":1},

    {"id":76,"name":"Tandoori Chicken","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g chicken legs\n1 cup yogurt\n1 tbsp tandoori masala\n1 tbsp lemon juice\n1 tsp chilli powder\n1 tbsp oil\nSalt to taste",
    "steps":"•Marinate chicken in yogurt, lemon juice, and spices for 4 hours.\n•Bake at 220°C for 25 minutes.\n•Brush with oil halfway.\n•Serve hot with salad and mint chutney.",
    "video_path":"",
    "is_default":1},

    {"id":77,"name":"Fish Fry","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n300g fish fillets\n1 tbsp ginger garlic paste\n1 tsp chilli powder\n1/2 tsp turmeric\n1 tbsp lemon juice\nRice flour for coating\nOil for frying\nSalt to taste",
    "steps":"•Marinate fish with spices and lemon.\n•Coat in rice flour.\n•Shallow fry till crisp.\n•Serve with onion rings."},

    {"id":78,"name":"Chicken Keema","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n400g minced chicken\n1 onion, chopped\n1 tomato, chopped\n1 tbsp ginger garlic paste\n1/2 tsp turmeric\n1 tsp garam masala\n1 tbsp oil\nSalt to taste",
    "steps":"•Heat oil, sauté onion and paste.\n•Add tomato, spices, and chicken mince.\n•Cook until dry and aromatic.\n•Serve with pav or paratha.",
    "video_path":"",
    "is_default":1},

    {"id":79,"name":"Mutton Biryani","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g mutton\n2 cups basmati rice\n2 onions\n1 cup yogurt\n1 tbsp ginger garlic paste\nWhole spices\nSalt, ghee, and herbs to taste",
    "steps":"•Cook mutton with spices till tender.\n•Layer with half-cooked rice, ghee, and herbs.\n•Steam 20 minutes.\n•Serve with onion raita.",
    "video_path":"",
    "is_default":1},

    {"id":80,"name":"Fish Tikka","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n300g fish cubes\n1/2 cup curd\n1 tbsp ginger garlic paste\n1 tsp garam masala\n1 tsp lemon juice\nSalt to taste",
    "steps":"•Marinate fish with curd and spices.\n•Skewer and grill 10–12 minutes.\n•Brush with butter and serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":81,"name":"Chicken Fried Rice","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n1 cup cooked rice\n1/2 cup shredded chicken\n1 egg\n1/2 cup mixed veggies\n1 tbsp soy sauce\nSalt and pepper\nOil for frying",
    "steps":"•Scramble egg and set aside.\n•Stir-fry vegetables and chicken.\n•Add rice, soy sauce, and egg.\n•Toss well and serve.",
    "video_path":"",
    "is_default":1},

    {"id":82,"name":"Prawn Fried Rice","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n1 cup rice\n100g prawns\n1/2 cup veggies\n1 tbsp soy sauce\n1 egg\nSalt and oil",
    "steps":"•Cook prawns till pink.\n•Add rice, veggies, soy sauce, and scrambled egg.\n•Toss well.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":83,"name":"Chicken Lollipop","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n8 chicken lollipops\n1/4 cup cornflour\n1 tbsp ginger garlic paste\n1 tbsp soy sauce\nSalt to taste\nOil for frying",
    "steps":"•Marinate lollipops with all ingredients.\n•Deep fry till golden.\n•Serve with schezwan sauce.",
    "video_path":"",
    "is_default":1},

    {"id":84,"name":"Fish Moilee","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n400g fish\n1 onion\n1 tomato\n1 cup coconut milk\n1 tsp mustard seeds\n1 tsp turmeric\nCurry leaves\nSalt and oil",
    "steps":"•Fry mustard seeds and curry leaves.\n•Add onion, tomato, and spices.\n•Pour coconut milk, add fish, simmer 10 minutes.\n•Serve with rice.",
    "video_path":"",
    "is_default":1},

    {"id":85,"name":"Chicken Curry","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g chicken\n2 onions\n2 tomatoes\n1 tbsp ginger garlic paste\n1 tsp garam masala\n1/2 tsp chilli powder\nOil and salt",
    "steps":"•Sauté onions and paste.\n•Add tomatoes and spices.\n•Add chicken, cook till done.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":86,"name":"Shrimp Coconut Curry","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n300g shrimp\n1 onion\n1 tomato\n1/2 cup coconut milk\n1 tsp curry powder\nSalt and oil",
    "steps":"•Sauté onion and tomato.\n•Add spices, coconut milk, and shrimp.\n•Simmer 8 minutes.\n•Serve with rice.",
    "video_path":"",
    "is_default":1},

    {"id":87,"name":"Egg Chicken Roll","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n2 parathas\n2 eggs\n1/2 cup cooked chicken pieces\nOnion, sauce, and spices\nOil for cooking",
    "steps":"•Make egg paratha.\n•Add cooked chicken and fillings.\n•Roll and serve.",
    "video_path":"",
    "is_default":1},

    {"id":88,"name":"Fish Cutlet","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n200g boiled fish\n1 boiled potato\n1 onion, chopped\n1 green chilli\n1 egg\nBreadcrumbs\nSalt and oil",
    "steps":"•Mash fish and potato with spices.\n•Shape cutlets, coat with egg and crumbs.\n•Fry till golden.\n•Serve with chutney.",
    "video_path":"",
    "is_default":1},

    {"id":89,"name":"Chicken Pakora","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n300g chicken\n1 cup gram flour\n1 tsp chilli powder\nSalt\nWater and oil for frying",
    "steps":"•Mix all ingredients into batter.\n•Deep fry chicken pieces till crisp.\n•Serve hot with sauce.",
    "video_path":"",
    "is_default":1},

    {"id":90,"name":"Mutton Keema Pav","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n400g minced mutton\n1 onion\n1 tomato\n1 tsp garam masala\nSalt\nOil for cooking",
    "steps":"•Cook keema with spices till dry.\n•Serve with buttered pav and lemon.",
    "video_path":"",
    "is_default":1},

    {"id":91,"name":"Chicken Momos","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n200g minced chicken\n1 onion\n1 carrot, grated\n1 tsp soy sauce\nDough for wrapper\nSalt and oil",
    "steps":"•Fill dumplings with chicken mixture.\n•Steam for 10 minutes.\n•Serve with spicy chutney.",
    "video_path":"",
    "is_default":1},

    {"id":92,"name":"Fish Curry with Tamarind","category":"NON-VEGETARIAN",
    "ingredients":"3 servings:\n300g fish\n1 onion\n1 tomato\n1 tbsp tamarind pulp\n1 tsp chilli powder\nSalt and oil",
    "steps":"•Sauté onion, add tomato and tamarind.\n•Add fish and cook till done.\n•Serve with rice.",
    "video_path":"",
    "is_default":1},

    {"id":93,"name":"Chicken Shawarma","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n200g chicken strips\n1 tsp garlic paste\n1 tsp lemon juice\n1 pita bread\nLettuce and sauce",
    "steps":"•Grill marinated chicken.\n•Stuff pita with chicken and veggies.\n•Wrap and serve.",
    "video_path":"",
    "is_default":1},

    {"id":94,"name":"Fish Biryani","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n400g fish\n2 cups basmati rice\n1 onion\n1 tomato\nSpices and ghee\nSalt to taste",
    "steps":"•Cook fish curry.\n•Layer with rice and ghee.\n•Steam 10 minutes.\n•Serve with raita.",
    "video_path":"",
    "is_default":1},

    {"id":95,"name":"Chicken Korma","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g chicken\n1/4 cup yogurt\n1 onion\n1 tbsp ginger garlic paste\n1/2 cup cashew paste\nSpices and ghee",
    "steps":"•Fry onion, add paste and yogurt.\n•Add chicken and cook till creamy.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":96,"name":"Mutton Rogan Josh","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n500g mutton\n1 onion\n1 tomato\n1 tbsp yogurt\n1 tsp garam masala\nSalt and oil",
    "steps":"•Cook mutton with yogurt and spices.\n•Simmer till tender.\n•Serve with naan.",
    "video_path":"",
    "is_default":1},

    {"id":97,"name":"Prawn Biryani","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n300g prawns\n2 cups rice\nOnions, tomato, and spices\nOil and salt",
    "steps":"•Cook prawns masala.\n•Layer with half-cooked rice.\n•Steam for 10 minutes.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":98,"name":"Chicken Nuggets","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n300g chicken mince\n1 egg\nBreadcrumbs\nSalt and pepper\nOil for frying",
    "steps":"•Shape mixture into nuggets.\n•Coat with egg and crumbs.\n•Fry till golden.",
    "video_path":"",
    "is_default":1},

    {"id":99,"name":"Fish Sandwich","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n2 fish fillets\nBread slices\nLettuce, tomato\nMayonnaise, salt, pepper",
    "steps":"•Cook fish fillets.\n•Assemble sandwich with veggies and mayo.\n•Serve fresh.",
    "video_path":"",
    "is_default":1},

    {"id":100,"name":"Garlic Butter Shrimp","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n200g shrimp\n2 tbsp butter\n4 garlic cloves\n1 tbsp lemon juice\nSalt and pepper",
    "steps":"•Melt butter, sauté garlic.\n•Add shrimp and cook 3–4 minutes.\n•Add lemon juice and serve.",
    "video_path":"",
    "is_default":1},

    {"id":101,"name":"Chicken Burger","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n200g chicken patty\n2 burger buns\nLettuce, tomato, cheese\nMayonnaise and ketchup",
    "steps":"•Cook patty on grill.\n•Assemble burger with toppings.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":102,"name":"Fish Tacos","category":"NON-VEGETARIAN",
    "ingredients":"2 servings:\n2 tortillas\n200g fish\n1/4 cup cabbage\n1 tbsp mayo\nLime juice and salt",
    "steps":"•Grill fish.\n•Assemble tacos with veggies and sauce.\n•Serve with lime wedges.",
    "video_path":"",
    "is_default":1},

    {"id":103,"name":"Chicken Pulao","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n400g chicken\n2 cups basmati rice\n1 onion\nWhole spices\nSalt, oil, and herbs",
    "steps":"•Sauté onion and spices.\n•Add chicken and rice.\n•Add water and cook till done.\n•Serve hot.",
    "video_path":"",
    "is_default":1},

    {"id":104,"name":"Fish Curry Kerala Style","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n400g fish\n1 onion\n1 tomato\n1 cup coconut milk\nCurry leaves and tamarind\nSpices and oil",
    "steps":"•Sauté onion and tomato.\n•Add coconut milk and spices.\n•Add fish, cook till done.\n•Serve with steamed rice.",
    "video_path":"",
    "is_default":1},

    {"id":105,"name":"Chicken Vindaloo","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n400g chicken\n2 onions\n2 tomatoes\nVinegar, garlic, and spices\nOil and salt",
    "steps":"•Marinate chicken in vinegar and spices.\n•Cook with onions and tomato.\n•Simmer till tender.\n•Serve spicy and hot.",
    "video_path":"",
    "is_default":1},

    {"id":106,"name":"Fish Finger","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n300g fish strips\n1 egg\nBreadcrumbs\nSalt, pepper\nOil for frying",
    "steps":"•Coat fish in egg and crumbs.\n•Deep fry till crisp.\n•Serve with tartar sauce.",
    "video_path":"",
    "is_default":1},

    {"id":107,"name":"Butter Garlic Chicken","category":"NON-VEGETARIAN",
    "ingredients":"4 servings:\n400g chicken\n2 tbsp butter\n4 garlic cloves\n1 tsp chilli flakes\nSalt and pepper",
    "steps":"•Melt butter, add garlic and chilli.\n•Cook chicken pieces till golden.\n•Serve with rice or noodles.",
    "video_path":"",
    "is_default":1}
]

os.makedirs(MEDIA_FOLDER, exist_ok=True)
df = pd.read_csv('recipes.csv')
if 'id' not in df.columns:
    df['id'] = range(1, len(df) + 1)
    df.to_csv('recipes.csv', index=False)


# ---------------------- DATA LAYER (pandas CSV) ----------------------

def ensure_csv_files():
    # recipes
    if not os.path.exists(RECIPES_CSV):
        df = pd.DataFrame(DEFAULT_RECIPES)
        df.to_csv(RECIPES_CSV, index=False)
    # recipe images
    if not os.path.exists(RECIPE_IMAGES_CSV):
        df = pd.DataFrame(columns=['id','recipe_id','file_path','caption'])
        df.to_csv(RECIPE_IMAGES_CSV, index=False)
    # step images
    if not os.path.exists(STEP_IMAGES_CSV):
        df = pd.DataFrame(columns=['id','recipe_id','step_index','file_path'])
        df.to_csv(STEP_IMAGES_CSV, index=False)


def load_recipes_df(category=None, search_term=None):
    df = pd.read_csv(RECIPES_CSV)
    if category:
        df = df[df['category'] == category]
    if search_term:
        mask = df['name'].str.contains(search_term, case=False, na=False) | df['ingredients'].str.contains(search_term, case=False, na=False)
        df = df[mask]
    df = df.sort_values('name')
    return df


def load_recipe_images(recipe_id):
    df = pd.read_csv(RECIPE_IMAGES_CSV)
    return df[df['recipe_id'] == recipe_id]


def load_step_images(recipe_id):
    df = pd.read_csv(STEP_IMAGES_CSV)
    return df[df['recipe_id'] == recipe_id]


def save_recipe(recipe):
    df = pd.read_csv(RECIPES_CSV)
    df = pd.concat([df, pd.DataFrame([recipe])], ignore_index=True)
    df.to_csv(RECIPES_CSV, index=False)


def save_recipe_image(entry):
    df = pd.read_csv(RECIPE_IMAGES_CSV)
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(RECIPE_IMAGES_CSV, index=False)


def save_step_image(entry):
    df = pd.read_csv(STEP_IMAGES_CSV)
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(STEP_IMAGES_CSV, index=False)


def delete_recipe_by_id(recipe_id):
    df = pd.read_csv(RECIPES_CSV)
    row = df[df['id'] == recipe_id]
    if row.empty:
        return False, 'Not found'
    if int(row.iloc[0]['is_default']) == 1:
        return False, 'Default recipes cannot be deleted.'
    df = df[df['id'] != recipe_id]
    df.to_csv(RECIPES_CSV, index=False)
    # remove media entries (and files) for that recipe
    img_df = pd.read_csv(RECIPE_IMAGES_CSV)
    rem = img_df[img_df['recipe_id'] == recipe_id]
    for p in rem['file_path'].tolist():
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
    img_df = img_df[img_df['recipe_id'] != recipe_id]
    img_df.to_csv(RECIPE_IMAGES_CSV, index=False)
    step_df = pd.read_csv(STEP_IMAGES_CSV)
    rem = step_df[step_df['recipe_id'] == recipe_id]
    for p in rem['file_path'].tolist():
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
    step_df = step_df[step_df['recipe_id'] != recipe_id]
    step_df.to_csv(STEP_IMAGES_CSV, index=False)
    return True, 'Deleted'

# ---------------------- UTILITIES ----------------------

def next_id(csv_path):
    if not os.path.exists(csv_path):
        return 1
    df = pd.read_csv(csv_path)
    if df.empty:
        return 1
    return int(df['id'].max()) + 1


def store_media_file(src_path):
    if not src_path or not os.path.exists(src_path):
        return None
    ext = os.path.splitext(src_path)[1]
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(MEDIA_FOLDER, new_name)
    shutil.copy2(src_path, dest)
    return dest


def load_image(path, size=None):
    if not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        try:
            return tk.PhotoImage(file=path)
        except Exception:
            return None

# ---------------------- GUI ----------------------
class SimpleKitchenApp:
    def __init__(self, root):
        ensure_csv_files()
        self.root = root
        root.title("The Simple Kitchen")
        icon_img = load_image(IMAGE_PATH_ICON)
        if icon_img:
            try:
                root.iconphoto(False, icon_img)
            except Exception:
                pass
        self.main_bg_img = load_image(IMAGE_PATH_MAIN_BG)
        if self.main_bg_img:
            bg_label = tk.Label(root, image=self.main_bg_img)
            bg_label.place(relwidth=1, relheight=1)
        else:
            root.configure(bg="#FDFBD4")
        open_btn = tk.Button(root, text="OPEN THE KITCHEN", bg="#B59D86", fg="#FDFBD4",
                             font=("Georgia", 20, "bold"), padx=170, pady=25,
                             command=self.open_categories, borderwidth=0, activebackground="#A08973")
        open_btn.place(relx=0.5, rely=0.7, anchor="center")

    def open_categories(self):
        CategoryWindow(self.root)

class CategoryWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("The Simple Kitchen")
        self.win.geometry("1366x768")
        icon_img = load_image(IMAGE_PATH_ICON)
        if icon_img:
            try:
                self.win.iconphoto(False, icon_img)
            except Exception:
                pass
        self.cat_bg_img = load_image(IMAGE_PATH_CAT_BG)
        if self.cat_bg_img:
            bg_label = tk.Label(self.win, image=self.cat_bg_img)
            bg_label.place(relwidth=1, relheight=1)
        else:
            self.win.configure(bg="#FFF7EE")
        categories = ["VEGETARIAN", "EGG-ETARIAN", "NON-VEGETARIAN"]
        for i, cat in enumerate(categories):
            lbl = tk.Label(self.win, text=cat, font=("Georgia", 64, "bold"), cursor="hand2",bg="#FDFBD4",fg="#B59D86",activebackground="#FDFBD4",activeforeground="#FFFFFF")
            lbl.place(relx=0.5, rely=0.2 + i * 0.3, anchor="center")
            lbl.bind("<Button-1>", lambda e, c=cat: self.open_menu(c))

    def open_menu(self, category):
        MenuWindow(self.win, category)

class MenuWindow:
    def __init__(self, parent, category):
        self.category = category
        self.win = tk.Toplevel(parent)
        self.win.title("The Simple Kitchen")
        self.win.geometry("1366x768")
        icon_img = load_image(IMAGE_PATH_ICON)
        if icon_img:
            try:
                self.win.iconphoto(False, icon_img)
            except Exception:
                pass
        left = tk.Frame(self.win, width=350)
        left.pack(side="left", fill="y", padx=10, pady=10)
        header = tk.Label(left, text=f"{self.category} RECIPES", font=("Georgia", 18, "bold"))
        header.pack(pady=5)
        search_frame = tk.Frame(left)
        search_frame.pack(pady=5, fill="x")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Georgia", 12))
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<KeyRelease>", lambda e: self.populate_list())
        search_btn = tk.Button(search_frame, text="Search", command=self.populate_list)
        search_btn.pack(side="right", padx=4)
        self.listbox = tk.Listbox(left, font=("Georgia", 12), width=40, height=25)
        self.listbox.pack(pady=5)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.view_selected())
        btn_frame = tk.Frame(left)
        btn_frame.pack(pady=8)
        view_btn = tk.Button(btn_frame, text="View", command=self.view_selected)
        view_btn.grid(row=0, column=0, padx=5)
        add_btn = tk.Button(btn_frame, text="Add Recipe", command=self.open_add_form)
        add_btn.grid(row=0, column=1, padx=5)
        del_btn = tk.Button(btn_frame, text="Delete", command=self.delete_selected)
        del_btn.grid(row=0, column=2, padx=5)
        back_btn = tk.Button(btn_frame, text="Back", command=self.win.destroy)
        back_btn.grid(row=0, column=3, padx=5)
        right = tk.Frame(self.win)
        right.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        self.detail_title = tk.Label(right, text="Select a recipe to view details", font=("Georgia", 16, "bold"))
        self.detail_title.pack(anchor="nw")
        media_frame = tk.Frame(right)
        media_frame.pack(fill="x", pady=5)
        self.recipe_image_label = tk.Label(media_frame)
        self.recipe_image_label.pack()
        self.detail_text = tk.Text(right, wrap="word", font=("Georgia", 12))
        self.detail_text.pack(expand=True, fill="both", pady=5)
        self.detail_text.configure(state="disabled")
        self.video_label = tk.Label(right, text="", fg="blue", cursor="hand2", font=("Georgia", 12, "underline"))
        self.video_label.pack(anchor="w")
        self.video_label.bind("<Button-1>", lambda e: self.open_video())
        self.current_recipe = None
        self.current_recipe_image = None
        self.video_file = None
        self.df = pd.DataFrame()
        self.populate_list()

    def populate_list(self):
        term = self.search_var.get().strip()
        self.df = load_recipes_df(category=self.category, search_term=term if term else None)
        self.listbox.delete(0, tk.END)
        for _, row in self.df.iterrows():
            self.listbox.insert(tk.END, f"{row['name']}")

    def view_selected(self):
        try:
            idx = self.listbox.curselection()
            if not idx:
                return
            name = self.listbox.get(idx[0])
            row = self.df[self.df['name'] == name].iloc[0]
            self.current_recipe = int(row['id'])
            title = row['name']
            ingredients = row['ingredients']
            steps = row['steps']
            video_path = row['video_path'] if 'video_path' in row and pd.notna(row['video_path']) else None
            self.detail_title.config(text=title)
            text = f"Ingredients:\n{ingredients}\n\nSteps:\n{steps}"
            self.detail_text.configure(state="normal")
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, text)
            self.detail_text.configure(state="disabled")
            imgs = load_recipe_images(self.current_recipe)
            if not imgs.empty:
                first = imgs.iloc[0]['file_path']
                img = load_image(first, size=(300,200))
                if img:
                    self.current_recipe_image = img
                    self.recipe_image_label.config(image=img)
                else:
                    self.recipe_image_label.config(image="", text="[Image not available]")
            else:
                self.recipe_image_label.config(image="", text="")
            if video_path and isinstance(video_path, str) and video_path.strip():
                self.video_label.config(text="Open recipe video")
                self.video_file = video_path
            else:
                self.video_label.config(text="")
                self.video_file = None
        except Exception as e:
            print("Error in view_selected:", e)

    def open_video(self):
        if not getattr(self, 'video_file', None):
            return
        path = self.video_file
        if not os.path.exists(path):
            messagebox.showerror("Missing file", "Video file not found on disk.")
            return
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                import subprocess
                subprocess.Popen(["xdg-open", path])
            else:
                messagebox.showinfo("Video", f"Video is at: {path}")
        except Exception as e:
            messagebox.showerror("Unable to open", str(e))

    def open_add_form(self):
        AddRecipeWindow(self.win, self)

    def delete_selected(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showinfo("Select", "Please select a recipe to delete.")
            return
        name = self.listbox.get(idx[0])
        row = self.df[self.df['name'] == name].iloc[0]
        recipe_id = int(row['id'])
        is_def = int(row['is_default']) if 'is_default' in row else 0
        if is_def == 1:
            messagebox.showwarning("Protected", "Default recipes cannot be deleted.")
            return
        if messagebox.askyesno("Confirm", f"Delete recipe '{name}' permanently?"):
            ok, msg = delete_recipe_by_id(recipe_id)
            if ok:
                messagebox.showinfo("Deleted", msg)
                self.populate_list()
                self.detail_title.config(text="Select a recipe to view details")
                self.detail_text.configure(state="normal")
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.configure(state="disabled")
                self.recipe_image_label.config(image="")
            else:
                messagebox.showerror("Error", msg)

class AddRecipeWindow:
    def __init__(self, parent, menu_window: MenuWindow):
        self.menu_window = menu_window
        self.win = tk.Toplevel(parent)
        self.win.title("Add Recipe - The Simple Kitchen")
        self.win.geometry("600x700")
        tk.Label(self.win, text="Recipe name:", font=("Georgia", 12)).pack(anchor="w", padx=10, pady=(10,0))
        self.name_entry = tk.Entry(self.win, font=("Georgia", 12))
        self.name_entry.pack(fill="x", padx=10)
        tk.Label(self.win, text="Category:", font=("Georgia", 12)).pack(anchor="w", padx=10, pady=(10,0))
        self.cat_var = tk.StringVar(value=self.menu_window.category)
        cat_menu = ttk.Combobox(self.win, textvariable=self.cat_var, values=["VEGETARIAN","EGG-ETARIAN","NON-VEGETARIAN"], state="readonly")
        cat_menu.pack(fill="x", padx=10)
        tk.Label(self.win, text="Ingredients (comma separated):", font=("Georgia", 12)).pack(anchor="w", padx=10, pady=(10,0))
        self.ing_text = tk.Text(self.win, height=4, font=("Georgia", 11))
        self.ing_text.pack(fill="x", padx=10)
        tk.Label(self.win, text="Steps (each step on a new line):", font=("Georgia", 12)).pack(anchor="w", padx=10, pady=(10,0))
        self.steps_text = tk.Text(self.win, height=8, font=("Georgia", 11))
        self.steps_text.pack(fill="both", padx=10, pady=(0,10), expand=False)
        tk.Label(self.win, text="Recipe images (optional):", font=("Georgia", 12)).pack(anchor="w", padx=10)
        self.recipe_images = []
        img_frame = tk.Frame(self.win)
        img_frame.pack(fill="x", padx=10)
        add_img_btn = tk.Button(img_frame, text="Add Image(s)", command=self.add_recipe_images)
        add_img_btn.pack(side="left")
        self.img_list_lbl = tk.Label(img_frame, text="No images selected", font=("Georgia", 10))
        self.img_list_lbl.pack(side="left", padx=8)
        tk.Label(self.win, text="Step images (optional):", font=("Georgia", 12)).pack(anchor="w", padx=10, pady=(10,0))
        step_img_frame = tk.Frame(self.win)
        step_img_frame.pack(fill="x", padx=10)
        self.step_images = {}
        add_step_img_btn = tk.Button(step_img_frame, text="Add Step Images", command=self.add_step_images)
        add_step_img_btn.pack(side="left")
        self.step_img_lbl = tk.Label(step_img_frame, text="No step images selected", font=("Georgia", 10))
        self.step_img_lbl.pack(side="left", padx=8)
        tk.Label(self.win, text="Optional recipe video (local file):", font=("Georgia", 12)).pack(anchor="w", padx=10, pady=(10,0))
        vid_frame = tk.Frame(self.win)
        vid_frame.pack(fill="x", padx=10)
        self.video_file = None
        add_vid_btn = tk.Button(vid_frame, text="Add Video", command=self.add_video)
        add_vid_btn.pack(side="left")
        self.vid_lbl = tk.Label(vid_frame, text="No video selected", font=("Georgia", 10))
        self.vid_lbl.pack(side="left", padx=8)
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=12)
        save_btn = tk.Button(btn_frame, text="Save", command=self.save_recipe)
        save_btn.grid(row=0, column=0, padx=6)
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.win.destroy)
        cancel_btn.grid(row=0, column=1, padx=6)

    def add_recipe_images(self):
        files = filedialog.askopenfilenames(title="Select Recipe Images", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.gif;*.bmp" )])
        if files:
            self.recipe_images.extend(files)
            self.img_list_lbl.config(text=f"{len(self.recipe_images)} image(s) selected")

    def add_step_images(self):
        steps_text = self.steps_text.get(1.0, tk.END).strip()
        if not steps_text:
            messagebox.showinfo("No steps", "Please enter steps first (each step on a new line) before adding images per step.")
            return
        steps = [s.strip() for s in steps_text.splitlines() if s.strip()]
        step_idx = simpledialog.askinteger("Step number", f"Enter step number (1..{len(steps)}) to attach images:")
        if not step_idx or step_idx < 1 or step_idx > len(steps):
            return
        files = filedialog.askopenfilenames(title=f"Select images for step {step_idx}", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.gif;*.bmp" )])
        if files:
            self.step_images.setdefault(step_idx, [])
            self.step_images[step_idx].extend(files)
            total = sum(len(v) for v in self.step_images.values())
            self.step_img_lbl.config(text=f"{total} step image(s) selected")

    def add_video(self):
        file = filedialog.askopenfilename(title="Select video file", filetypes=[("Video files","*.mp4;*.mov;*.avi;*.mkv;*.wmv" )])
        if file:
            self.video_file = file
            self.vid_lbl.config(text=os.path.basename(file))

    def save_recipe(self):
        name = self.name_entry.get().strip()
        category = self.cat_var.get().strip()
        ingredients = self.ing_text.get(1.0, tk.END).strip()
        steps = self.steps_text.get(1.0, tk.END).strip()
        if not name or not category or not ingredients or not steps:
            messagebox.showwarning("Missing fields", "Please fill in all fields before saving.")
            return
        # prepare recipe entry
        rid = next_id(RECIPES_CSV)
        recipe = {
            'id': rid,
            'name': name,
            'category': category,
            'ingredients': ingredients,
            'steps': steps,
            'video_path': '',
            'is_default': 0
        }
        # save recipe
        save_recipe(recipe)
        # save images
        for f in self.recipe_images:
            dest = store_media_file(f)
            if dest:
                rid_img = next_id(RECIPE_IMAGES_CSV)
                save_recipe_image({'id': rid_img, 'recipe_id': rid, 'file_path': dest, 'caption': ''})
        for step_idx, files in self.step_images.items():
            for f in files:
                dest = store_media_file(f)
                if dest:
                    sid = next_id(STEP_IMAGES_CSV)
                    save_step_image({'id': sid, 'recipe_id': rid, 'step_index': int(step_idx), 'file_path': dest})
        if self.video_file:
            dest = store_media_file(self.video_file)
            if dest:
                df = pd.read_csv(RECIPES_CSV)
                df.loc[df['id'] == rid, 'video_path'] = dest
                df.to_csv(RECIPES_CSV, index=False)
        messagebox.showinfo("Saved", "Recipe saved successfully.")
        self.menu_window.populate_list()
        self.win.destroy()

# ---------------------- RUN APP ----------------------
if __name__ == "__main__":
    ensure_csv_files()
    root = tk.Tk()
    root.geometry("900x700")
    app = SimpleKitchenApp(root)
    root.mainloop()
