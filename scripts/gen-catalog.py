#!/usr/bin/env python3
"""
Generate a realistic mock catalog for Yellow Bee.

This stands in for a real Star-Plus item-file export so the catalog page can be
designed and built before the POS connection exists. Field names deliberately
mirror what a grocery POS item file actually carries, so swapping in real data
is a mapping job, not a rewrite.
"""
import json
import re
import random

random.seed(4242)  # deterministic output so rebuilds don't churn the diff

# (name, brand, size, low_price, high_price)
CATALOG = {
    "Rice & Grains": [
        ("Jasmine Rice", "Three Ladies", ["5 lb", "25 lb", "50 lb"], 9.99, 62.99),
        ("Sushi Rice", "Kokuho Rose", ["5 lb", "15 lb"], 12.99, 34.99),
        ("Calrose Rice", "Nishiki", ["5 lb", "15 lb"], 11.49, 32.99),
        ("Sweet Glutinous Rice", "Three Ladies", ["2 lb", "5 lb"], 5.99, 12.99),
        ("Brown Jasmine Rice", "Dynasty", ["5 lb"], 13.49, 13.49),
        ("Basmati Rice", "Royal", ["5 lb", "10 lb"], 12.99, 22.99),
        ("Black Forbidden Rice", "Lotus Foods", ["15 oz"], 6.49, 6.49),
        ("Red Cargo Rice", "Golden Phoenix", ["5 lb"], 14.99, 14.99),
        ("Rice Flour", "Erawan", ["16 oz"], 2.29, 2.29),
        ("Glutinous Rice Flour", "Erawan", ["16 oz"], 2.49, 2.49),
        ("Tapioca Starch", "Erawan", ["16 oz"], 2.19, 2.19),
        ("Pearl Barley", "Assi", ["16 oz"], 3.49, 3.49),
        ("Millet", "Assi", ["16 oz"], 3.99, 3.99),
        ("Mung Beans", "Golden Bell", ["14 oz", "2 lb"], 3.29, 7.99),
        ("Red Adzuki Beans", "Golden Bell", ["14 oz"], 3.79, 3.79),
        ("Job's Tears", "Assi", ["16 oz"], 4.49, 4.49),
    ],
    "Noodles": [
        ("Rice Vermicelli", "Three Ladies", ["16 oz"], 2.49, 2.49),
        ("Banh Pho Rice Sticks", "Three Ladies", ["14 oz"], 2.79, 2.79),
        ("Pad Thai Rice Noodles", "Chantaboon", ["16 oz"], 3.29, 3.29),
        ("Udon Noodles", "Myojo", ["7 oz", "3-pack"], 2.99, 6.49),
        ("Fresh Udon", "Twin Marquis", ["14 oz"], 3.99, 3.99),
        ("Soba Buckwheat Noodles", "Hakubaku", ["9.5 oz"], 4.99, 4.99),
        ("Somen Noodles", "Myojo", ["16 oz"], 4.49, 4.49),
        ("Glass Noodles", "Longkou", ["8 oz"], 2.99, 2.99),
        ("Sweet Potato Noodles", "Assi", ["16 oz"], 6.49, 6.49),
        ("Egg Noodles", "Twin Marquis", ["14 oz"], 3.49, 3.49),
        ("Wonton Wrappers", "Twin Marquis", ["12 oz"], 3.29, 3.29),
        ("Dumpling Wrappers", "Twin Marquis", ["16 oz"], 3.79, 3.79),
        ("Spring Roll Wrappers", "Spring Home", ["8 oz"], 4.29, 4.29),
        ("Rice Paper Wrappers", "Three Ladies", ["12 oz"], 3.49, 3.49),
        ("Knife Cut Noodles", "Assi", ["16 oz"], 4.99, 4.99),
        ("Ramen Noodles Fresh", "Sun Noodle", ["2-pack"], 5.49, 5.49),
    ],
    "Instant Ramen": [
        ("Shin Ramyun", "Nongshim", ["Single", "5-pack"], 1.79, 8.49),
        ("Shin Ramyun Black", "Nongshim", ["Single", "4-pack"], 2.49, 10.99),
        ("Buldak Hot Chicken", "Samyang", ["Single", "5-pack"], 2.29, 10.49),
        ("Buldak Carbonara", "Samyang", ["Single", "5-pack"], 2.29, 10.49),
        ("Buldak 2x Spicy", "Samyang", ["Single", "5-pack"], 2.49, 11.49),
        ("Chapagetti", "Nongshim", ["Single", "4-pack"], 1.89, 7.99),
        ("Neoguri Seafood", "Nongshim", ["Single", "4-pack"], 1.89, 7.99),
        ("Jin Ramen Mild", "Ottogi", ["Single", "5-pack"], 1.59, 7.49),
        ("Jin Ramen Spicy", "Ottogi", ["Single", "5-pack"], 1.59, 7.49),
        ("Cup Noodles", "Nissin", ["Single"], 1.49, 1.49),
        ("Demae Ramen", "Nissin", ["Single", "5-pack"], 1.29, 6.29),
        ("Mi Goreng Fried Noodle", "Indomie", ["Single", "5-pack"], 0.99, 4.79),
        ("Tom Yum Instant Noodle", "Mama", ["Single", "6-pack"], 0.79, 4.49),
        ("Bun Bo Hue Instant", "Vifon", ["Single"], 1.19, 1.19),
        ("Pho Bo Instant Bowl", "Vifon", ["Single"], 2.29, 2.29),
        ("Kimchi Ramyun", "Paldo", ["Single", "5-pack"], 1.69, 7.99),
        ("Bibim Men Cold Noodle", "Paldo", ["Single", "5-pack"], 1.99, 9.49),
        ("Jjajangmyeon", "Paldo", ["Single"], 1.99, 1.99),
    ],
    "Sauces & Condiments": [
        ("Premium Soy Sauce", "Lee Kum Kee", ["16.9 oz", "33.8 oz"], 4.49, 7.99),
        ("Dark Soy Sauce", "Pearl River Bridge", ["16.9 oz"], 3.99, 3.99),
        ("Light Soy Sauce", "Pearl River Bridge", ["16.9 oz"], 3.79, 3.79),
        ("Naturally Brewed Soy Sauce", "Kikkoman", ["10 oz", "20 oz"], 3.99, 6.49),
        ("Less Sodium Soy Sauce", "Kikkoman", ["15 oz"], 5.49, 5.49),
        ("Oyster Sauce", "Lee Kum Kee", ["18 oz", "32 oz"], 4.99, 7.99),
        ("Vegetarian Stir-Fry Sauce", "Lee Kum Kee", ["17 oz"], 5.49, 5.49),
        ("Hoisin Sauce", "Lee Kum Kee", ["20 oz"], 4.79, 4.79),
        ("Chili Garlic Sauce", "Huy Fong", ["8 oz", "18 oz"], 3.49, 5.99),
        ("Sriracha Hot Chili Sauce", "Huy Fong", ["17 oz", "28 oz"], 4.99, 7.49),
        ("Sambal Oelek", "Huy Fong", ["8 oz", "18 oz"], 3.29, 5.79),
        ("Fish Sauce", "Three Crabs", ["24 oz"], 6.99, 6.99),
        ("Fish Sauce Premium", "Red Boat", ["8.45 oz"], 9.99, 9.99),
        ("Fish Sauce", "Golden Boy", ["24 oz"], 4.99, 4.99),
        ("Japanese Mayonnaise", "Kewpie", ["12 oz", "17.6 oz"], 5.49, 7.49),
        ("Ponzu Citrus Sauce", "Kikkoman", ["10 oz"], 4.99, 4.99),
        ("Teriyaki Marinade", "Kikkoman", ["10 oz"], 4.29, 4.29),
        ("Gochujang Red Pepper Paste", "Chung Jung One", ["1.1 lb", "2.2 lb"], 6.99, 11.99),
        ("Ssamjang Seasoned Paste", "Chung Jung One", ["1.1 lb"], 6.49, 6.49),
        ("Doenjang Soybean Paste", "Chung Jung One", ["1.1 lb"], 6.99, 6.99),
        ("Miso Paste White", "Hikari", ["17.6 oz"], 6.49, 6.49),
        ("Miso Paste Red", "Hikari", ["17.6 oz"], 6.49, 6.49),
        ("Black Bean Garlic Sauce", "Lee Kum Kee", ["8 oz"], 3.99, 3.99),
        ("XO Sauce", "Lee Kum Kee", ["7.8 oz"], 12.99, 12.99),
        ("Chili Crisp", "Lao Gan Ma", ["7.4 oz"], 4.99, 4.99),
        ("Chili Oil with Peanuts", "Lao Gan Ma", ["7.4 oz"], 4.99, 4.99),
        ("Sweet Chili Sauce", "Mae Ploy", ["12 oz", "32 oz"], 3.49, 6.99),
        ("Red Curry Paste", "Mae Ploy", ["14 oz"], 3.99, 3.99),
        ("Green Curry Paste", "Mae Ploy", ["14 oz"], 3.99, 3.99),
        ("Panang Curry Paste", "Mae Ploy", ["14 oz"], 3.99, 3.99),
        ("Massaman Curry Paste", "Maesri", ["4 oz"], 1.99, 1.99),
        ("Tamarind Concentrate", "Cock Brand", ["16 oz"], 3.49, 3.49),
        ("Hot Pot Base Spicy", "Haidilao", ["7 oz"], 4.49, 4.49),
        ("Mala Hot Pot Base", "Little Sheep", ["8.4 oz"], 4.99, 4.99),
        ("Seasoned Seaweed Sauce", "Chinsu", ["8 oz"], 3.29, 3.29),
        ("Chili Sauce", "Chinsu", ["8.8 oz"], 2.99, 2.99),
        ("Yellow Bean Sauce", "Koon Chun", ["13 oz"], 3.79, 3.79),
        ("Double Black Soy", "Koon Chun", ["15 oz"], 4.49, 4.49),
    ],
    "Oils & Vinegar": [
        ("Toasted Sesame Oil", "Kadoya", ["5.5 oz", "11 oz"], 5.49, 8.99),
        ("Pure Sesame Oil", "Lee Kum Kee", ["7 oz"], 5.99, 5.99),
        ("Rice Bran Oil", "Tsuno", ["33.8 oz"], 11.99, 11.99),
        ("Vegetable Oil", "Happy Family", ["48 oz"], 5.49, 5.49),
        ("Coconut Oil", "Chaokoh", ["16 oz"], 7.99, 7.99),
        ("Rice Vinegar", "Marukan", ["12 oz", "24 oz"], 3.29, 5.49),
        ("Seasoned Rice Vinegar", "Marukan", ["12 oz"], 3.79, 3.79),
        ("Black Vinegar", "Chinkiang", ["18.6 oz"], 3.49, 3.49),
        ("White Rice Vinegar", "Koon Chun", ["16 oz"], 2.99, 2.99),
        ("Coconut Vinegar", "Datu Puti", ["12 oz"], 2.49, 2.49),
        ("Cane Vinegar", "Silver Swan", ["12 oz"], 2.29, 2.29),
        ("Mirin Sweet Cooking Wine", "Kikkoman", ["10 oz"], 4.49, 4.49),
        ("Shaoxing Cooking Wine", "Pagoda", ["21 oz"], 4.99, 4.99),
        ("Cooking Sake", "Takara", ["12.7 oz"], 5.99, 5.99),
    ],
    "Canned & Jarred": [
        ("Coconut Milk", "Chaokoh", ["13.5 oz", "5.6 oz"], 1.99, 3.49),
        ("Coconut Milk", "Aroy-D", ["14 oz", "33.8 oz"], 2.29, 4.99),
        ("Coconut Cream", "Aroy-D", ["14 oz"], 2.79, 2.79),
        ("Bamboo Shoots Sliced", "Aroy-D", ["8 oz", "20 oz"], 1.79, 3.29),
        ("Water Chestnuts Sliced", "Dynasty", ["8 oz"], 1.99, 1.99),
        ("Straw Mushrooms", "Aroy-D", ["15 oz"], 2.49, 2.49),
        ("Baby Corn", "Aroy-D", ["15 oz"], 2.29, 2.29),
        ("Lychee in Syrup", "Aroy-D", ["20 oz"], 3.49, 3.49),
        ("Longan in Syrup", "Aroy-D", ["20 oz"], 3.49, 3.49),
        ("Jackfruit in Syrup", "Aroy-D", ["20 oz"], 3.79, 3.79),
        ("Rambutan in Syrup", "Aroy-D", ["20 oz"], 3.79, 3.79),
        ("Toddy Palm Seed", "Aroy-D", ["20 oz"], 3.49, 3.49),
        ("Grass Jelly", "Chin Chin", ["19 oz"], 2.29, 2.29),
        ("Sweet Corn Cream Style", "Aroy-D", ["15 oz"], 2.19, 2.19),
        ("Roasted Eel", "Kawasho", ["3.5 oz"], 6.99, 6.99),
        ("Sardines in Tomato", "Ligo", ["5.5 oz"], 1.99, 1.99),
        ("Spam Classic", "Hormel", ["12 oz"], 4.79, 4.79),
        ("Spam Less Sodium", "Hormel", ["12 oz"], 4.99, 4.99),
        ("Pickled Radish", "Assi", ["17 oz"], 3.49, 3.49),
        ("Kimchi Napa Cabbage", "Chongga", ["14 oz", "28 oz"], 5.99, 10.99),
        ("Kimchi Radish Cubed", "Chongga", ["17.6 oz"], 6.49, 6.49),
        ("Pickled Mustard Greens", "Golden Bell", ["12 oz"], 2.79, 2.79),
        ("Century Eggs", "Golden Bell", ["6-pack"], 5.99, 5.99),
        ("Salted Duck Eggs", "Golden Bell", ["6-pack"], 5.49, 5.49),
    ],
    "Snacks": [
        ("Pocky Chocolate", "Glico", ["1.41 oz"], 2.29, 2.29),
        ("Pocky Strawberry", "Glico", ["1.41 oz"], 2.29, 2.29),
        ("Pocky Matcha", "Glico", ["1.41 oz"], 2.49, 2.49),
        ("Pocky Cookies & Cream", "Glico", ["1.41 oz"], 2.49, 2.49),
        ("Hello Panda Chocolate", "Meiji", ["2.1 oz"], 2.19, 2.19),
        ("Hello Panda Strawberry", "Meiji", ["2.1 oz"], 2.19, 2.19),
        ("Yan Yan Chocolate", "Meiji", ["1.7 oz"], 1.99, 1.99),
        ("Shrimp Chips", "Calbee", ["3.3 oz"], 2.99, 2.99),
        ("Hot & Spicy Shrimp Chips", "Calbee", ["3.3 oz"], 2.99, 2.99),
        ("Honey Butter Chip", "Haitai", ["2.3 oz"], 3.49, 3.49),
        ("Shrimp Crackers", "Nongshim", ["2.6 oz"], 2.49, 2.49),
        ("Onion Rings Snack", "Nongshim", ["2.6 oz"], 2.49, 2.49),
        ("Turtle Chips Corn", "Orion", ["5 oz"], 3.99, 3.99),
        ("Choco Pie", "Orion", ["12-pack"], 6.49, 6.49),
        ("Custard Cake", "Lotte", ["6-pack"], 5.99, 5.99),
        ("Pepero Original", "Lotte", ["1.4 oz"], 1.99, 1.99),
        ("Pepero Almond", "Lotte", ["1.4 oz"], 2.19, 2.19),
        ("Rice Crackers Senbei", "Kameda", ["7 oz"], 4.49, 4.49),
        ("Kaki no Tane", "Kameda", ["4.2 oz"], 3.99, 3.99),
        ("Wasabi Green Peas", "Hapi", ["4.9 oz"], 2.79, 2.79),
        ("Coated Peanuts Coconut", "Koh-Kae", ["3.5 oz"], 1.99, 1.99),
        ("Coated Peanuts BBQ", "Koh-Kae", ["3.5 oz"], 1.99, 1.99),
        ("Rice Cracker Mix", "Want Want", ["5.6 oz"], 3.29, 3.29),
        ("Senbei Rice Crackers", "Want Want", ["3.2 oz"], 2.49, 2.49),
        ("Seaweed Snack Original", "Gim", ["5-pack"], 3.99, 3.99),
        ("Seaweed Snack Sesame", "Gim", ["5-pack"], 4.29, 4.29),
        ("Dried Squid Shredded", "Golden Bell", ["1.7 oz"], 6.99, 6.99),
        ("Prawn Crackers Uncooked", "Golden Bell", ["8 oz"], 3.49, 3.49),
        ("Banana Chips", "Bonita", ["6 oz"], 2.99, 2.99),
        ("Taro Chips", "Bonita", ["6 oz"], 3.29, 3.29),
        ("Jackfruit Chips", "Bonita", ["3.5 oz"], 4.49, 4.49),
        ("Corn Puff Snack", "Nongshim", ["2.6 oz"], 2.29, 2.29),
        ("Pea Crackers", "Calbee", ["2.8 oz"], 2.79, 2.79),
        ("Sesame Crackers", "Nissin", ["3.5 oz"], 2.99, 2.99),
    ],
    "Candy & Sweets": [
        ("Hi-Chew Strawberry", "Morinaga", ["1.76 oz"], 1.99, 1.99),
        ("Hi-Chew Mango", "Morinaga", ["1.76 oz"], 1.99, 1.99),
        ("Hi-Chew Green Apple", "Morinaga", ["1.76 oz"], 1.99, 1.99),
        ("Hi-Chew Assorted Bag", "Morinaga", ["12.7 oz"], 7.99, 7.99),
        ("Milk Candy", "White Rabbit", ["6.3 oz"], 4.49, 4.49),
        ("Botan Rice Candy", "JFC", ["0.75 oz"], 1.49, 1.49),
        ("Koala's March Chocolate", "Lotte", ["1.6 oz"], 2.19, 2.19),
        ("Kasugai Gummy Lychee", "Kasugai", ["3.77 oz"], 3.49, 3.49),
        ("Kasugai Gummy Peach", "Kasugai", ["3.77 oz"], 3.49, 3.49),
        ("Kasugai Gummy Muscat", "Kasugai", ["3.77 oz"], 3.49, 3.49),
        ("Matcha KitKat", "Nestle Japan", ["4.5 oz"], 8.99, 8.99),
        ("Strawberry KitKat", "Nestle Japan", ["4.5 oz"], 8.99, 8.99),
        ("Mochi Ice Cream Assorted", "My/Mo", ["6-pack"], 6.99, 6.99),
        ("Red Bean Mochi", "Royal Family", ["7.4 oz"], 3.99, 3.99),
        ("Peanut Mochi", "Royal Family", ["7.4 oz"], 3.99, 3.99),
        ("Haw Flakes", "Golden Bell", ["5-pack"], 1.99, 1.99),
        ("Dried Mango", "Philippine Brand", ["3.5 oz", "7 oz"], 3.99, 6.99),
        ("Preserved Plum", "Golden Bell", ["4 oz"], 3.49, 3.49),
        ("Ginger Chews", "Prince of Peace", ["4 oz"], 2.99, 2.99),
    ],
    "Beverages": [
        ("Yakult Probiotic Drink", "Yakult", ["5-pack"], 4.49, 4.49),
        ("Vita Lemon Tea", "Vitasoy", ["8.45 oz", "6-pack"], 1.29, 6.49),
        ("Vita Chrysanthemum Tea", "Vitasoy", ["8.45 oz", "6-pack"], 1.29, 6.49),
        ("Soy Milk Original", "Vitasoy", ["8.45 oz", "6-pack"], 1.29, 6.49),
        ("Milkis Soda", "Lotte", ["8.45 oz"], 1.49, 1.49),
        ("Ramune Original", "Sangaria", ["6.76 oz"], 2.49, 2.49),
        ("Ramune Strawberry", "Sangaria", ["6.76 oz"], 2.49, 2.49),
        ("Ramune Melon", "Sangaria", ["6.76 oz"], 2.49, 2.49),
        ("Pocari Sweat", "Otsuka", ["16.9 oz"], 2.29, 2.29),
        ("Aloe Vera Drink Original", "OKF", ["16.9 oz"], 1.99, 1.99),
        ("Aloe Vera Drink Mango", "OKF", ["16.9 oz"], 1.99, 1.99),
        ("Grass Jelly Drink", "Chin Chin", ["10.7 oz"], 1.79, 1.79),
        ("Coconut Water with Pulp", "Foco", ["17.5 oz"], 2.29, 2.29),
        ("Basil Seed Drink", "Foco", ["10.8 oz"], 1.99, 1.99),
        ("Chrysanthemum Tea", "Foco", ["10.8 oz"], 1.79, 1.79),
        ("Winter Melon Tea", "Foco", ["10.8 oz"], 1.79, 1.79),
        ("Sugarcane Juice", "Foco", ["10.8 oz"], 1.99, 1.99),
        ("Soursop Nectar", "Foco", ["11.8 oz"], 1.99, 1.99),
        ("Lychee Juice", "Foco", ["11.8 oz"], 1.99, 1.99),
        ("Calpico Original", "Calpis", ["16.9 oz"], 3.49, 3.49),
        ("Sac Sac Orange", "Lotte", ["8.4 oz"], 1.99, 1.99),
        ("Banana Milk", "Binggrae", ["6.8 oz", "6-pack"], 1.79, 9.49),
        ("Strawberry Milk", "Binggrae", ["6.8 oz"], 1.79, 1.79),
        ("Melon Milk", "Binggrae", ["6.8 oz"], 1.79, 1.79),
        ("Sparkling Yuzu", "Sangaria", ["11.5 oz"], 2.79, 2.79),
        ("Thai Iced Tea Mix", "Pantai", ["16 oz"], 5.49, 5.49),
    ],
    "Tea & Coffee": [
        ("Vietnamese Coffee Ground", "Trung Nguyen", ["8.8 oz"], 8.99, 8.99),
        ("Creative No.1 Coffee", "Trung Nguyen", ["8.8 oz"], 9.99, 9.99),
        ("G7 Instant Coffee 3-in-1", "Trung Nguyen", ["20-pack"], 7.99, 7.99),
        ("Coffee with Chicory", "Cafe Du Monde", ["15 oz"], 8.49, 8.49),
        ("Phin Coffee Filter", "Trung Nguyen", ["Each"], 4.99, 4.99),
        ("Jasmine Green Tea", "Ten Ren", ["8 oz"], 9.99, 9.99),
        ("Oolong Tea Loose Leaf", "Ten Ren", ["8 oz"], 12.99, 12.99),
        ("Genmaicha Green Tea", "Yamamotoyama", ["1.4 oz"], 5.99, 5.99),
        ("Sencha Green Tea Bags", "Yamamotoyama", ["20-count"], 4.99, 4.99),
        ("Barley Tea", "Dongsuh", ["30-count"], 4.49, 4.49),
        ("Corn Silk Tea", "Dongsuh", ["30-count"], 4.99, 4.99),
        ("Buckwheat Tea", "Dongsuh", ["30-count"], 4.99, 4.99),
        ("Matcha Powder Culinary", "Aiya", ["3.5 oz"], 14.99, 14.99),
        ("Chrysanthemum Flower Tea", "Golden Bell", ["3.5 oz"], 5.49, 5.49),
        ("Pu-erh Tea Cake", "Golden Bell", ["12.5 oz"], 18.99, 18.99),
        ("Thai Tea Loose Leaf", "Pantai", ["14 oz"], 6.99, 6.99),
        ("Boba Tapioca Pearls", "WuFuYuan", ["8.8 oz"], 3.99, 3.99),
        ("Instant Boba Kit", "Bossen", ["Kit"], 12.99, 12.99),
    ],
    "Frozen": [
        ("Pork & Vegetable Dumplings", "Bibigo", ["24 oz"], 9.99, 9.99),
        ("Chicken Dumplings", "Bibigo", ["24 oz"], 9.99, 9.99),
        ("Kimchi Dumplings", "Bibigo", ["24 oz"], 9.99, 9.99),
        ("Soup Dumplings Xiao Long Bao", "Synear", ["14 oz"], 7.99, 7.99),
        ("Shrimp Shumai", "Feng Wei", ["16 oz"], 8.49, 8.49),
        ("Har Gow Shrimp Dumplings", "Feng Wei", ["16 oz"], 9.49, 9.49),
        ("Pork Buns Char Siu Bao", "Feng Wei", ["12 oz"], 6.99, 6.99),
        ("Steamed Custard Buns", "Feng Wei", ["12 oz"], 6.49, 6.49),
        ("Spring Rolls Vegetable", "Spring Home", ["22 oz"], 7.49, 7.49),
        ("Egg Rolls Pork", "Golden Bell", ["16 oz"], 6.99, 6.99),
        ("Scallion Pancakes", "Twin Marquis", ["16 oz"], 5.99, 5.99),
        ("Roti Paratha", "Kawan", ["14 oz"], 5.49, 5.49),
        ("Mochi Ice Cream Green Tea", "My/Mo", ["6-pack"], 6.99, 6.99),
        ("Red Bean Popsicle", "Lotte", ["6-pack"], 5.99, 5.99),
        ("Melona Melon Bar", "Binggrae", ["8-pack"], 7.49, 7.49),
        ("Frozen Durian", "Golden Bell", ["14 oz"], 12.99, 12.99),
        ("Frozen Jackfruit", "Golden Bell", ["16 oz"], 6.99, 6.99),
        ("Frozen Banana Leaves", "Golden Bell", ["16 oz"], 3.99, 3.99),
        ("Frozen Edamame", "Kahiki", ["16 oz"], 3.99, 3.99),
        ("Frozen Taro Chunks", "Golden Bell", ["16 oz"], 4.49, 4.49),
        ("Fish Balls", "Golden Bell", ["16 oz"], 6.49, 6.49),
        ("Beef Balls", "Golden Bell", ["16 oz"], 7.49, 7.49),
        ("Sliced Beef Hot Pot", "Golden Bell", ["16 oz"], 12.99, 12.99),
        ("Sliced Pork Belly Hot Pot", "Golden Bell", ["16 oz"], 10.99, 10.99),
        ("Rice Cake Tteokbokki", "Assi", ["21 oz"], 5.49, 5.49),
    ],
    "Fresh Produce": [
        ("Baby Bok Choy", "Local", ["lb"], 2.49, 2.49),
        ("Shanghai Bok Choy", "Local", ["lb"], 2.29, 2.29),
        ("Gai Lan Chinese Broccoli", "Local", ["lb"], 3.49, 3.49),
        ("Yu Choy", "Local", ["lb"], 2.99, 2.99),
        ("Napa Cabbage", "Local", ["lb"], 1.49, 1.49),
        ("Daikon Radish", "Local", ["lb"], 1.79, 1.79),
        ("Korean Radish", "Local", ["lb"], 1.99, 1.99),
        ("Thai Basil", "Local", ["bunch"], 2.49, 2.49),
        ("Cilantro", "Local", ["bunch"], 1.29, 1.29),
        ("Green Onion", "Local", ["bunch"], 1.29, 1.29),
        ("Lemongrass", "Local", ["each"], 0.99, 0.99),
        ("Galangal", "Local", ["lb"], 6.99, 6.99),
        ("Ginger Root", "Local", ["lb"], 3.49, 3.49),
        ("Thai Chili Peppers", "Local", ["4 oz"], 2.99, 2.99),
        ("Jalapeno Peppers", "Local", ["lb"], 2.49, 2.49),
        ("Shiitake Mushrooms Fresh", "Local", ["8 oz"], 4.49, 4.49),
        ("Enoki Mushrooms", "Local", ["7 oz"], 2.29, 2.29),
        ("King Oyster Mushrooms", "Local", ["lb"], 5.99, 5.99),
        ("Bean Sprouts", "Local", ["lb"], 1.79, 1.79),
        ("Chinese Eggplant", "Local", ["lb"], 2.99, 2.99),
        ("Bitter Melon", "Local", ["lb"], 3.49, 3.49),
        ("Winter Melon", "Local", ["lb"], 1.99, 1.99),
        ("Taro Root", "Local", ["lb"], 2.99, 2.99),
        ("Lotus Root", "Local", ["lb"], 4.99, 4.99),
        ("Asian Pear", "Local", ["each"], 2.49, 2.49),
        ("Longan Fresh", "Local", ["lb"], 8.99, 8.99),
        ("Lychee Fresh", "Local", ["lb"], 9.99, 9.99),
        ("Young Coconut", "Local", ["each"], 3.99, 3.99),
        ("Dragon Fruit", "Local", ["each"], 4.99, 4.99),
        ("Mango Ataulfo", "Local", ["each"], 1.99, 1.99),
        ("Persimmon Fuyu", "Local", ["each"], 1.79, 1.79),
        ("Jujube Dates Fresh", "Local", ["lb"], 6.99, 6.99),
    ],
    "Meat & Seafood": [
        ("Pork Belly Sliced", "Butcher", ["lb"], 7.99, 7.99),
        ("Pork Shoulder", "Butcher", ["lb"], 5.49, 5.49),
        ("Ground Pork", "Butcher", ["lb"], 5.99, 5.99),
        ("Beef Brisket", "Butcher", ["lb"], 11.99, 11.99),
        ("Beef Short Rib Bone-In", "Butcher", ["lb"], 15.99, 15.99),
        ("Ribeye Thin Sliced", "Butcher", ["lb"], 16.99, 16.99),
        ("Chicken Thigh Boneless", "Butcher", ["lb"], 4.99, 4.99),
        ("Chicken Wings", "Butcher", ["lb"], 4.49, 4.49),
        ("Whole Chicken", "Butcher", ["lb"], 3.29, 3.29),
        ("Tilapia Whole", "Seafood", ["lb"], 6.99, 6.99),
        ("Branzino Whole", "Seafood", ["lb"], 12.99, 12.99),
        ("Salmon Fillet", "Seafood", ["lb"], 14.99, 14.99),
        ("Shrimp 16/20 Shell-On", "Seafood", ["lb"], 12.99, 12.99),
        ("Shrimp Peeled Deveined", "Seafood", ["lb"], 14.99, 14.99),
        ("Squid Tubes", "Seafood", ["lb"], 8.99, 8.99),
        ("Octopus Frozen", "Seafood", ["lb"], 13.99, 13.99),
        ("Manila Clams", "Seafood", ["lb"], 7.99, 7.99),
        ("Mussels", "Seafood", ["lb"], 5.99, 5.99),
        ("Live Dungeness Crab", "Seafood", ["lb"], 18.99, 18.99),
    ],
    "Tofu & Soy": [
        ("Firm Tofu", "House Foods", ["14 oz"], 2.49, 2.49),
        ("Extra Firm Tofu", "House Foods", ["14 oz"], 2.49, 2.49),
        ("Silken Tofu", "House Foods", ["12 oz"], 2.29, 2.29),
        ("Medium Firm Tofu", "Pulmuone", ["14 oz"], 2.79, 2.79),
        ("Fried Tofu Puffs", "Golden Bell", ["7 oz"], 3.49, 3.49),
        ("Tofu Skin Sheets", "Golden Bell", ["8 oz"], 4.99, 4.99),
        ("Pressed Tofu Seasoned", "Golden Bell", ["8 oz"], 3.99, 3.99),
        ("Natto Fermented Soybeans", "Mitoku", ["3-pack"], 3.49, 3.49),
        ("Soy Milk Unsweetened", "Pulmuone", ["32 oz"], 4.49, 4.49),
        ("Tempeh", "Lightlife", ["8 oz"], 3.99, 3.99),
    ],
    "Spices & Seasoning": [
        ("Five Spice Powder", "Golden Bell", ["3 oz"], 2.99, 2.99),
        ("Sichuan Peppercorn", "Golden Bell", ["2 oz"], 4.99, 4.99),
        ("Star Anise Whole", "Golden Bell", ["2 oz"], 3.99, 3.99),
        ("Gochugaru Chili Flakes", "Chung Jung One", ["1 lb"], 9.99, 9.99),
        ("White Pepper Ground", "Golden Bell", ["3 oz"], 3.49, 3.49),
        ("Curry Powder", "S&B", ["3.2 oz"], 4.49, 4.49),
        ("Furikake Rice Seasoning", "Nagatanien", ["1.7 oz"], 3.99, 3.99),
        ("Shichimi Togarashi", "S&B", ["0.52 oz"], 4.29, 4.29),
        ("Wasabi Paste", "S&B", ["1.52 oz"], 3.49, 3.49),
        ("Dashi Stock Powder", "Ajinomoto", ["1.76 oz"], 5.49, 5.49),
        ("MSG Umami Seasoning", "Ajinomoto", ["8 oz"], 3.99, 3.99),
        ("Chicken Bouillon Powder", "Knorr", ["8 oz"], 4.49, 4.49),
        ("Pho Spice Packet", "Gia Vi", ["1 oz"], 2.49, 2.49),
        ("Dried Shiitake Mushrooms", "Golden Bell", ["3 oz"], 6.99, 6.99),
        ("Dried Shrimp", "Golden Bell", ["3 oz"], 7.99, 7.99),
        ("Dried Anchovies", "Assi", ["8 oz"], 8.99, 8.99),
        ("Kombu Dried Kelp", "Emerald Cove", ["1.76 oz"], 6.49, 6.49),
        ("Bonito Flakes", "Marutomo", ["1.76 oz"], 5.99, 5.99),
        ("Nori Sheets Roasted", "Yamamotoyama", ["10-sheet"], 4.99, 4.99),
        ("Wood Ear Mushrooms Dried", "Golden Bell", ["2 oz"], 4.49, 4.49),
        ("Rock Sugar", "Golden Bell", ["16 oz"], 3.49, 3.49),
        ("Palm Sugar", "Cock Brand", ["16 oz"], 4.29, 4.29),
    ],
    "Bakery & Baking": [
        ("Sweet Rice Flour Mochiko", "Koda Farms", ["16 oz"], 4.49, 4.49),
        ("All Purpose Flour", "Happy Family", ["5 lb"], 4.99, 4.99),
        ("Potato Starch", "Erawan", ["16 oz"], 2.99, 2.99),
        ("Corn Starch", "Happy Family", ["16 oz"], 2.29, 2.29),
        ("Red Bean Paste", "Shirakiku", ["17.6 oz"], 4.99, 4.99),
        ("Black Sesame Paste", "Golden Bell", ["10.5 oz"], 6.49, 6.49),
        ("Condensed Milk", "Longevity", ["14 oz"], 2.79, 2.79),
        ("Evaporated Milk", "Carnation", ["12 oz"], 1.99, 1.99),
        ("Pandan Extract", "Koepoe", ["1 oz"], 2.49, 2.49),
        ("Coconut Cream Powder", "Chaokoh", ["2 oz"], 1.79, 1.79),
        ("Agar Agar Powder", "Telephone", ["1 oz"], 2.29, 2.29),
        ("Sponge Cake Slice", "In-House", ["each"], 3.50, 3.50),
        ("Egg Tart", "In-House", ["each"], 2.75, 2.75),
        ("Pineapple Bun", "In-House", ["each"], 2.50, 2.50),
        ("Milk Bread Loaf", "In-House", ["each"], 5.99, 5.99),
    ],
    "Household": [
        ("Bamboo Chopsticks", "Home", ["10-pair"], 3.99, 3.99),
        ("Melamine Rice Bowl", "Home", ["each"], 4.99, 4.99),
        ("Bamboo Steamer 10 inch", "Home", ["each"], 16.99, 16.99),
        ("Carbon Steel Wok 14 inch", "Home", ["each"], 29.99, 29.99),
        ("Wok Spatula", "Home", ["each"], 9.99, 9.99),
        ("Rice Paddle", "Home", ["each"], 2.99, 2.99),
        ("Ramen Bowl Ceramic", "Home", ["each"], 12.99, 12.99),
        ("Soup Spoon Ceramic", "Home", ["each"], 2.49, 2.49),
        ("Dish Soap", "Joy", ["30 oz"], 4.49, 4.49),
        ("Paper Towels", "Bounty", ["6-roll"], 11.99, 11.99),
        ("Trash Bags", "Glad", ["45-count"], 12.99, 12.99),
        ("Aluminum Foil", "Reynolds", ["75 sq ft"], 6.49, 6.49),
        ("Plastic Wrap", "Glad", ["200 sq ft"], 5.49, 5.49),
        ("Incense Sticks", "Home", ["40-count"], 3.99, 3.99),
    ],
    "Health & Beauty": [
        ("Tiger Balm Red", "Tiger Balm", ["0.63 oz"], 8.99, 8.99),
        ("Tiger Balm White", "Tiger Balm", ["0.63 oz"], 8.99, 8.99),
        ("Medicated Oil", "Eagle Brand", ["0.8 oz"], 6.99, 6.99),
        ("White Flower Oil", "Hoe Hin", ["0.67 oz"], 7.99, 7.99),
        ("Sheet Mask Aloe", "Innisfree", ["each"], 2.49, 2.49),
        ("Sheet Mask Green Tea", "Innisfree", ["each"], 2.49, 2.49),
        ("Rice Water Cleanser", "The Face Shop", ["5 oz"], 9.99, 9.99),
        ("Sunscreen SPF 50", "Biore", ["1.7 oz"], 12.99, 12.99),
        ("Hand Cream", "Kracie", ["1.2 oz"], 5.99, 5.99),
        ("Toothpaste Bamboo Salt", "LG", ["4.5 oz"], 4.99, 4.99),
        ("Herbal Tea Cold Relief", "Prince of Peace", ["10-bag"], 5.49, 5.49),
        ("Ginseng Extract", "Prince of Peace", ["30-vial"], 19.99, 19.99),
    ],
}

# Aisle map — a real store would carry this in the POS item file.
AISLES = {
    "Rice & Grains": "Aisle 1",
    "Noodles": "Aisle 1",
    "Instant Ramen": "Aisle 2",
    "Sauces & Condiments": "Aisle 3",
    "Oils & Vinegar": "Aisle 3",
    "Canned & Jarred": "Aisle 4",
    "Snacks": "Aisle 5",
    "Candy & Sweets": "Aisle 5",
    "Beverages": "Aisle 6",
    "Tea & Coffee": "Aisle 6",
    "Frozen": "Frozen",
    "Fresh Produce": "Produce",
    "Meat & Seafood": "Butcher",
    "Tofu & Soy": "Refrigerated",
    "Spices & Seasoning": "Aisle 7",
    "Bakery & Baking": "Aisle 7",
    "Household": "Aisle 8",
    "Health & Beauty": "Aisle 8",
}

# Categories where items are sold by weight — these can never carry a truthful
# integer unit count, which matters for how the site renders availability.
WEIGHED = {"Fresh Produce", "Meat & Seafood"}

# Country of origin, keyed by brand. Asian markets label this heavily and
# shoppers genuinely sort on it. A real POS carries it as a item-file column.
ORIGIN = {
    "Three Ladies": "Thailand", "Kokuho Rose": "USA", "Nishiki": "USA",
    "Dynasty": "USA", "Royal": "India", "Lotus Foods": "USA",
    "Golden Phoenix": "Thailand", "Erawan": "Thailand", "Assi": "Korea",
    "Golden Bell": "China", "Chantaboon": "Thailand", "Myojo": "Japan",
    "Twin Marquis": "USA", "Hakubaku": "Japan", "Longkou": "China",
    "Spring Home": "Singapore", "Sun Noodle": "USA", "Nongshim": "Korea",
    "Samyang": "Korea", "Ottogi": "Korea", "Nissin": "Japan",
    "Indomie": "Indonesia", "Mama": "Thailand", "Vifon": "Vietnam",
    "Paldo": "Korea", "Lee Kum Kee": "Hong Kong", "Pearl River Bridge": "China",
    "Kikkoman": "Japan", "Huy Fong": "USA", "Three Crabs": "Thailand",
    "Red Boat": "Vietnam", "Golden Boy": "Thailand", "Kewpie": "Japan",
    "Chung Jung One": "Korea", "Hikari": "Japan", "Lao Gan Ma": "China",
    "Mae Ploy": "Thailand", "Maesri": "Thailand", "Cock Brand": "Thailand",
    "Haidilao": "China", "Little Sheep": "China", "Chinsu": "Vietnam",
    "Koon Chun": "Hong Kong", "Kadoya": "Japan", "Tsuno": "Japan",
    "Happy Family": "USA", "Chaokoh": "Thailand", "Marukan": "Japan",
    "Chinkiang": "China", "Datu Puti": "Philippines", "Silver Swan": "Philippines",
    "Pagoda": "China", "Takara": "Japan", "Aroy-D": "Thailand",
    "Chin Chin": "Taiwan", "Kawasho": "Japan", "Ligo": "Philippines",
    "Hormel": "USA", "Chongga": "Korea", "Glico": "Japan", "Meiji": "Japan",
    "Calbee": "Japan", "Haitai": "Korea", "Orion": "Korea", "Lotte": "Korea",
    "Kameda": "Japan", "Hapi": "Japan", "Koh-Kae": "Thailand",
    "Want Want": "Taiwan", "Gim": "Korea", "Bonita": "Philippines",
    "Morinaga": "Japan", "White Rabbit": "China", "JFC": "Japan",
    "Kasugai": "Japan", "Nestle Japan": "Japan", "My/Mo": "USA",
    "Royal Family": "Taiwan", "Philippine Brand": "Philippines",
    "Prince of Peace": "USA", "Yakult": "Japan", "Vitasoy": "Hong Kong",
    "Sangaria": "Japan", "Otsuka": "Japan", "OKF": "Korea", "Foco": "Thailand",
    "Calpis": "Japan", "Binggrae": "Korea", "Pantai": "Thailand",
    "Trung Nguyen": "Vietnam", "Cafe Du Monde": "USA", "Ten Ren": "Taiwan",
    "Yamamotoyama": "Japan", "Dongsuh": "Korea", "Aiya": "Japan",
    "WuFuYuan": "China", "Bossen": "USA", "Bibigo": "Korea", "Synear": "China",
    "Feng Wei": "China", "Kawan": "Malaysia", "Kahiki": "USA",
    "House Foods": "USA", "Pulmuone": "Korea", "Mitoku": "Japan",
    "Lightlife": "USA", "S&B": "Japan", "Nagatanien": "Japan",
    "Ajinomoto": "Japan", "Knorr": "USA", "Gia Vi": "Vietnam",
    "Emerald Cove": "USA", "Marutomo": "Japan", "Koda Farms": "USA",
    "Shirakiku": "Japan", "Carnation": "USA", "Longevity": "USA",
    "Koepoe": "Indonesia", "Telephone": "Thailand", "Tiger Balm": "Singapore",
    "Eagle Brand": "Singapore", "Hoe Hin": "Hong Kong", "Innisfree": "Korea",
    "The Face Shop": "Korea", "Biore": "Japan", "Kracie": "Japan", "LG": "Korea",
    "Local": "Washington", "Butcher": "Washington", "Seafood": "Washington",
    "In-House": "Made here", "Home": "", "Joy": "USA", "Bounty": "USA",
    "Glad": "USA", "Reynolds": "USA",
}

# Weekly ad window. A real feed would carry per-item start/end dates; the mock
# runs one store-wide window, which is how a small market actually operates.
SALE_ENDS = "July 27"


def snap_price(target):
    """
    Snap a computed sale price to a grocery-style ending (.99/.79/.49/.29).

    Always rounds DOWN to the nearest valid ending so a "25% off" tag can never
    produce a price above what the math promised.
    """
    endings = [0.99, 0.79, 0.49, 0.29]
    whole = int(target)
    candidates = [whole + e for e in endings] + [whole - 1 + e for e in endings]
    valid = [c for c in candidates if c <= target and c > 0]
    return round(max(valid), 2) if valid else round(target, 2)


def unit_price(price, size):
    """
    Derive a $/oz, $/lb, or $/each figure from the pack size.

    Real grocery shelves are required to post unit pricing in many
    jurisdictions, and it is the single best signal for comparing a 5 lb bag
    against a 25 lb one. Returns None when the size string has no parseable
    quantity ("Kit", "bunch", "each").
    """

    s = size.strip().lower()

    m = re.match(r"^([\d.]+)\s*(oz|lb)$", s)
    if m:
        qty, unit = float(m.group(1)), m.group(2)
        if qty > 0:
            return {"value": round(price / qty, 2), "unit": unit}

    m = re.match(r"^([\d.]+)[-\s](pack|count|vial|pair|sheet)$", s)
    if m:
        qty = float(m.group(1))
        if qty > 0:
            return {"value": round(price / qty, 2), "unit": "ea"}

    return None


items = []
sku_n = 100000

for category, entries in CATALOG.items():
    for (name, brand, sizes, lo, hi) in entries:
        for i, size in enumerate(sizes):
            sku_n += 7
            # interpolate price across the size range
            if len(sizes) == 1:
                list_price = lo
            else:
                t = i / (len(sizes) - 1)
                list_price = round(lo + (hi - lo) * t, 2)

            # A small share of items are seasonal/special-order in any real store.
            roll = random.random()
            if roll < 0.06:
                availability = "seasonal"
            elif roll < 0.10:
                availability = "ask"
            else:
                availability = "stocked"

            # ~17% of the shelf is on the weekly ad at any given time. Seasonal
            # and special-order items never go on ad.
            on_sale = availability == "stocked" and random.random() < 0.17
            if on_sale:
                pct = random.choice([0.10, 0.15, 0.20, 0.25, 0.30, 0.35])
                price = snap_price(list_price * (1 - pct))
                # snap_price never rounds up, but guard the floor anyway so a
                # sub-dollar item can't land at or above its own list price.
                if price >= list_price:
                    price = round(max(0.29, list_price - 0.30), 2)
                saved = round(list_price - price, 2)
                # Loss-leader style limits show up on the deepest discounts.
                limit = random.choice([None, None, "Limit 4", "Limit 2"]) if pct >= 0.25 else None
            else:
                price = list_price
                saved = 0.0
                limit = None

            item = {
                "sku": str(sku_n),
                "name": name,
                "brand": brand,
                "category": category,
                "aisle": AISLES[category],
                "size": size,
                "price": price,
                "listPrice": list_price,
                "onSale": on_sale,
                "saved": saved,
                "savedPct": round(saved / list_price * 100) if on_sale and list_price else 0,
                "limit": limit,
                "byWeight": category in WEIGHED,
                "availability": availability,
                "origin": ORIGIN.get(brand, ""),
                "isNew": random.random() < 0.05,
                "popular": random.random() < 0.09,
            }

            up = unit_price(price, size)
            if up:
                item["unitPrice"] = up["value"]
                item["unitMeasure"] = up["unit"]

            items.append(item)

items.sort(key=lambda x: (x["category"], x["name"], x["size"]))

categories = []
for category in CATALOG.keys():
    cat_items = [i for i in items if i["category"] == category]
    categories.append({
        "name": category,
        "aisle": AISLES[category],
        "count": len(cat_items),
        "onSale": sum(1 for i in cat_items if i["onSale"]),
    })

on_sale_items = [i for i in items if i["onSale"]]
# Lead the weekly ad with the biggest savings, the way a circular does.
deals = sorted(on_sale_items, key=lambda x: -x["saved"])[:12]

out = {
    "_comment": (
        "MOCK DATA. Stands in for a Star-Plus item-file export until the POS "
        "connection exists. Field names mirror a real grocery POS item file so "
        "swapping in live data is a mapping job. price/listPrice map to the "
        "Sale and List price types Star-Plus already carries. Regenerate with "
        "scripts/gen-catalog.py."
    ),
    "source": "mock",
    "updated": "2026-07-21",
    "saleEnds": SALE_ENDS,
    "stats": {
        "items": len(items),
        "categories": len(categories),
        "onSale": len(on_sale_items),
        "newItems": sum(1 for i in items if i["isNew"]),
    },
    "categories": categories,
    "deals": [d["sku"] for d in deals],
    "items": items,
}

path = "/Users/mjbutler35/Documents/GitHub/yellow-bee/data/catalog-mock.json"
with open(path, "w") as f:
    json.dump(out, f, indent=2)

print(f"{len(items)} items across {len(categories)} categories")
for c in categories:
    print(f"  {c['count']:4d}  {c['name']}")
