import json
import pathlib
import argparse


# Recursively adds enum entry to all object properties named target_property in
# schema_object
def add_enums(schema_object, target_property, enum):
    
    if(schema_object['type'] == 'array'):
        schema_object['items'] = add_enums(schema_object['items'], target_property, enum)
        
    if(schema_object['type'] in ['string', 'boolean', 'integer']):
        return(schema_object)
    
    if(schema_object['type'] == 'object'):    
        if(target_property in schema_object['properties']):
            if(schema_object['properties'][target_property]['type'] == 'array'):
                schema_object['properties'][target_property]['items']['enum'] = enum
            else:
                schema_object['properties'][target_property]['enum'] = enum

        for object_property in schema_object['properties']:
            schema_object['properties'][object_property] = add_enums(schema_object['properties'][object_property], target_property, enum)
    
    return(schema_object)


# Recursively adds enum entry to all object properties named target property
# with parent object property named parent property in schema_object
def add_enums_with_parent(schema_object, property_parent, target_property, enum):
    
    if(schema_object['type'] in ['string', 'boolean', 'integer']):
        return(schema_object)
    
    if(schema_object['type'] == 'array'):
        schema_object['items'] = add_enums_with_parent(schema_object['items'], property_parent, target_property, enum)
    
    if(schema_object['type'] == 'object'):
        if(property_parent in schema_object['properties']):
            add_enums(schema_object['properties'][property_parent], target_property, enum)
    
    return(schema_object)


# Applies add_enum to specified schema file given target property name and
# desired enum
def write_enums(schema_filename, target_property, enum):
    with open(schema_filename) as f:
        schema_object = json.load(f)
    schema_object = add_enums(schema_object, target_property, enum)
    with open(schema_filename, 'w') as f:
        json.dump(schema_object, f, indent = 4)


# Applies add_enum to specified schema file given parent property and target
# property name and desired enum
def write_enums_with_parent(schema_filename, property_parent, target_property, enum):
    with open(schema_filename) as f:
        schema_object = json.load(f)
    schema_object = add_enums_with_parent(schema_object, property_parent, target_property, enum)
    with open(schema_filename, 'w') as f:
        json.dump(schema_object, f, indent = 4)


# Load or define enums

def get_rings(data_dir):
    with open(data_dir.joinpath('json/rings.json')) as f:
        rings = json.load(f)
    rings_enum = [ ring['name'] for ring in rings ]

    return rings_enum


def get_clans(data_dir):
    with open(data_dir.joinpath('json/clans.json')) as f:
        clans = json.load(f)
    clans_enum = [ clan['name'] for clan in clans ]
    
    return clans_enum


def get_skills(data_dir):
    with open(data_dir.joinpath('json/skill_groups.json')) as f:
        skill_groups = json.load(f)
    skill_groups_enum = [ skill_group['name'] for skill_group in skill_groups ]
    skills_enum = [ skill for skill_group in skill_groups for skill in skill_group['skills'] ]

    return skill_groups_enum, skills_enum


def get_techniques(data_dir):
    with open(data_dir.joinpath('json/techniques.json')) as f:
        technique_categories = json.load(f)
    technique_categories_enum = [
        category['name'] for category in technique_categories
    ]
    technique_subcategories_enum = [
        subcategory['name']
        for category in technique_categories
        for subcategory in category['subcategories']
        if subcategory['name'] != ''
    ]
    techniques_enum = [
        technique['name']
        for category in technique_categories
        for subcategory in category['subcategories']
        for technique in subcategory['techniques']
    ]

    return technique_categories_enum, technique_subcategories_enum, techniques_enum


def get_qualities(data_dir):
    with open(data_dir.joinpath('json/qualities.json')) as f:
        qualities = json.load(f)

    qualities_enum = [ quality['name'] for quality in qualities ]
    
    return qualities_enum


def get_equipment(data_dir):

    # Load armour
    with open(data_dir.joinpath('json/armor.json')) as f:
        armor = json.load(f)
    armor_enum = [ item['name'] for item in armor ]

    # Load weapons
    with open(data_dir.joinpath('json/weapons.json')) as f:
        weapon_categories = json.load(f)
    weapons_enum = [
        weapon['name']
        for weapon_category in weapon_categories
        for weapon in weapon_category['entries']
    ]

    # Load personal effects
    with open(data_dir.joinpath('json/personal_effects.json')) as f:
        personal_effects = json.load(f)
    personal_effects_enum = [ personal_effect['name'] for personal_effect in personal_effects ]

    # Combine into equipment
    equipment_enum = armor_enum + weapons_enum + personal_effects_enum
    
    return equipment_enum


def get_books():
    books_enum = ['Core', 'EE', 'SL']

    return books_enum


def get_resistance():
    resistance_enum = ['Physical', 'Supernatural']

    return resistance_enum


def get_currency():
    currency_enum = ['koku', 'bu', 'zeni']

    return currency_enum


# Write enums to schemas

def write_rings(data_dir, rings_enum):

    print('Writing rings ...')

    print('... to clans')
    write_enums(
        data_dir.joinpath('json_schema/clans.schema.json'),
        'ring_increase',
        rings_enum
    )

    print('... to advantages/disadavantages')
    write_enums(
        data_dir.joinpath('json_schema/advantages_disadvantages.schema.json'),
        'ring',
        rings_enum
    )

    print('... to schools')
    write_enums(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'ring_increase',
        rings_enum + ['any']
    )

    return rings_enum


def write_clans(data_dir, clans_enum):

    print('Writing clans ...')

    print('... to schools')
    write_enums(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'clan',
        clans_enum
    )

    return clans_enum


def write_skills(data_dir, skills_enum):

    print('Writing skills ...')

    print('... to clans')
    write_enums(
        data_dir.joinpath('json_schema/clans.schema.json'),
        'skill_increase',
        skills_enum
    )

    print('... to school starting skills')
    write_enums_with_parent(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'starting_skills',
        'set',
        skills_enum
    )


def write_techniques(data_dir, techniques_enum, technique_categories_enum):

    print('Writing technique categories to school available techniques')
    write_enums(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'techniques_available',
        technique_categories_enum
    )

    print('Writing techniques to school starting techniques')
    write_enums_with_parent(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'starting_techniques',
        'set',
        techniques_enum
    )


def write_qualities(data_dir, qualities_enum):

    print('Writing qualities ...')

    print('... to armor')
    write_enums(
        data_dir.joinpath('json_schema/armor.schema.json'),
        'qualities',
        qualities_enum
    )

    print('... to personal effects')
    write_enums(
        data_dir.joinpath('json_schema/personal_effects.schema.json'),
        'qualities',
        qualities_enum
    )

    print('... to weapons')
    write_enums(
        data_dir.joinpath('json_schema/weapons.schema.json'),
        'qualities',
        qualities_enum
    )


def write_equipment(data_dir, equipment_enum):

    print('Writing equipment to school starting outfit')
    write_enums_with_parent(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'starting_outfit',
        'set',
        (
            equipment_enum +
            [
                "Traveling Pack",
                "Two Weapons of Rarity 6 or Lower",
                "One Weapon of Rarity 6 or Lower",
                "Two Items of Rarity 4 or Lower"
            ]
        )
    )


def write_books(data_dir, books_enum):

    print('Writing books ...')

    print('... to clans')
    write_enums(
        data_dir.joinpath('json_schema/clans.schema.json'),
        'book',
        books_enum
    )

    print('... to advantages/disadvantages')
    write_enums(
        data_dir.joinpath('json_schema/advantages_disadvantages.schema.json'),
        'book',
        books_enum
    )

    print('... to armor')
    write_enums(
        data_dir.joinpath('json_schema/armor.schema.json'),
        'book',
        books_enum
    )

    print('... to personal effects')
    write_enums(
        data_dir.joinpath('json_schema/personal_effects.schema.json'),
        'book',
        books_enum
    )

    print('... to weapons')
    write_enums(
        data_dir.joinpath('json_schema/weapons.schema.json'),
        'book',
        books_enum
    )

    print('... to schools')
    write_enums(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'book',
        books_enum
    )


def write_resistance(data_dir, resistance_enum):

    print('Writing resistance to armor')
    write_enums(
        data_dir.joinpath('json_schema/armor.schema.json'),
        'category',
        resistance_enum
    )


def write_currency(data_dir, currency_enum):

    print('Writing currency ...')

    print('... to armor')
    write_enums(
        data_dir.joinpath('json_schema/armor.schema.json'),
        'unit',
        currency_enum
    )

    print('... to personal effects')
    write_enums(
        data_dir.joinpath('json_schema/personal_effects.schema.json'),
        'unit',
        currency_enum
    )

    print('... to weapons')
    write_enums(
        data_dir.joinpath('json_schema/weapons.schema.json'),
        'unit',
        currency_enum
    )


def write_advance(data_dir, skill_groups_enum, skills_enum, technique_categories_enum, technique_subcategories_enum, techniques_enum):

    print('Writing skills, skill groups, technique categories and techniques to school curriculum advance')
    write_enums(
        data_dir.joinpath('json_schema/schools.schema.json'),
        'advance',
        skill_groups_enum + skills_enum + technique_categories_enum + technique_subcategories_enum + techniques_enum
    )


def main(option):

    # Get path to data directory
    data_dir = pathlib.Path(__file__).parents[1]

    # Write enums if they were requested
    if option is None or 'rings' in option:
        write_rings(data_dir, get_rings(data_dir))
    if option is None or 'clans' in option:
        write_clans(data_dir, get_clans(data_dir))
    if option is None or 'skills' in option:
        skill_groups_enum, skills_enum = get_skills(data_dir)
        write_skills(data_dir, skills_enum)
    if option is None or 'techniques' in option:
        technique_categories_enum, technique_subcategories_enum, techniques_enum = get_techniques(data_dir)
        write_techniques(data_dir, techniques_enum, technique_categories_enum)
    if option is None or 'qualities' in option:
        write_qualities(data_dir, get_qualities(data_dir))
    if option is None or 'equipment' in option:
        write_equipment(data_dir, get_equipment(data_dir))
    if option is None or 'books' in option:
        write_books(data_dir, get_books())
    if option is None or 'resistance' in option:
        write_resistance(data_dir, get_resistance())
    if option is None or 'currency' in option:
        write_currency(data_dir, get_currency())
    if option is None or 'skills' in option or 'techniques' in option:
        write_advance(data_dir, skill_groups_enum, skills_enum, technique_categories_enum, technique_subcategories_enum, techniques_enum)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Utility to add enums to json schema')
    parser.add_argument(
        '--option',
        nargs = '*',
        choices = ['rings', 'clans', 'skills', 'techniques', 'qualities', 'equipment', 'books', 'resistance', 'currency'],
        help = 'Which enums you want to write to json schemas (defaults to all with no arguments specified)'
    )
    args = parser.parse_args()

    main(args.option)
