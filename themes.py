"""Find thematic Wordle-in-One puzzles: clue and target from the same theme.

usage: python3 themes.py [THEME ...] [--min N] [--max N] [--list]

Edit THEMES below to add your own. Any word can be a clue; only words on the
answer list (data/answers.txt) can be targets.
"""
import argparse
from collections import defaultdict
from pathlib import Path
from wio_core import score, load

THEMES = {
    'food': 'apple bagel bacon berry bread candy cocoa cream crepe curry dough flour fudge grape gravy guava '
            'honey lemon mango maple melon mocha olive onion pasta peach pecan pizza salad salsa sauce scone '
            'spice steak sugar sushi syrup taffy toast wheat cider latte gumbo jelly juice kebab nacho sweet '
            'treat icing torte tripe chili cumin basil thyme',
    'animals': 'bison camel eagle egret finch goose heron horse hyena koala lemur llama moose mouse otter panda '
               'raven rhino robin shark sheep skunk sloth snail snake squid stork tiger viper whale zebra dingo '
               'gecko goat bunny puppy kitty swine hound beast crane louse',
    'spooky': 'ghost ghoul witch demon devil crypt skull bones mummy curse spell coven haunt scary eerie gloom '
              'grave tomb fiend beast creep',
    'music': 'piano organ cello viola banjo flute opera tenor choir chord chant psalm hymn music lyric rhyme '
             'tempo bass drum metal disco tango salsa waltz rumba polka blues',
    'weather': 'storm cloud rainy sunny windy foggy frost snowy sleet flood humid chill gusty misty muggy',
    'royal': 'queen crown royal regal reign realm baron count duchy noble manor tiara',
    'body': 'heart blood brain spine bones skull liver colon chest elbow ankle wrist thumb mouth tooth teeth '
            'femur tibia nerve',
    'water': 'ocean beach shore coast river delta creek brook swamp marsh water wharf canal bayou flood tidal',
    'emotion': 'happy angry irate weepy jolly merry sulky moody tense upset proud shame guilt grief bliss',
    'military': 'troop squad navy medal honor valor siege tower sword spear knife blade lance rifle arrow',
    'cards': 'poker joker queen spade heart trump bluff deuce',
    'lodging': 'hotel motel lodge cabin manor villa house tower',
    'space': 'orbit comet lunar solar alien probe rover earth venus',
    'fantasy': 'magic spell witch fairy pixie gnome dwarf giant troll elfin',
    'colors': 'amber azure beige black brown coral cream ebony green ivory khaki lemon lilac mauve ochre '
              'olive peach rouge sepia taupe umber white mocha slate',
    'sports': 'rugby skate coach pitch field court score medal relay racer caddy serve rally match arena '
              'squad bowls kayak cleat',
    'clothing': 'shirt skirt dress pants scarf glove shoes boots socks jeans tunic smock apron cloak shawl '
                'beret frock parka thong',
    'tools': 'drill lathe level ruler plane clamp spade shear hoist tongs auger knife wedge screw nails '
             'gauge vices',
    'kitchen': 'spoon ladle knife plate bowls stove grill whisk sieve tongs range fryer mixer baker glass '
               'apron broil',
    'jobs': 'nurse medic pilot judge baker clerk coach miner tutor actor agent chefs guard scout cadet mason '
            'usher valet nanny vicar rabbi',
    'vehicles': 'truck plane train coach yacht canoe kayak buggy wagon sedan lorry ferry barge motor cycle '
                'rover',
    'trees': 'maple cedar birch aspen alder beech larch olive grove woody acorn bough trunk stump sprig '
             'piney leafy',
    'flowers': 'daisy tulip lilac poppy peony aster bloom petal lotus thorn pansy sepal stalk roses',
    'gems': 'pearl jewel agate topaz beryl amber coral stone carat flint ingot metal steel opals',
    'money': 'money funds bonus price loans asset debit audit stock share bonds penny token wager lucre '
             'broke cents',
    'crime': 'thief steal fraud crook rogue heist guilt felon judge trial court alibi plead swear bribe '
             'theft cheat',
    'school': 'class pupil tutor grade study exams essay chalk teach learn ruler paper books spell',
    'science': 'atoms laser quark ozone genes virus cells helix prism orbit solar fungi algae phase ratio',
    'computers': 'pixel mouse modem cache debug input logic cyber bytes macro email emoji query array click',
    'office': 'clerk staff memos paper desks chair badge filer agent shift email inbox audit stamp',
    'furniture': 'chair table couch stool bench shelf divan futon sofas chest cribs lamps desks crate',
    'house': 'attic porch floor doors roofs walls stair foyer manor lodge cabin villa condo house shack',
    'garden': 'plant seeds hoses rakes shrub hedge lawns mower bloom fence grass vines weeds petal daisy',
    'farm': 'sheep goats chick plows barns field wheat silos mules horse ranch crops grain',
    'birds': 'eagle raven robin finch goose heron stork crane egret quail swans hawks doves macaw gulls',
    'sealife': 'shark whale squid prawn coral krill trout perch guppy conch clams otter seals pikes',
    'insects': 'louse midge aphid fleas gnats wasps moths roach larva mites drone swarm hives stung bites '
               'queen',
    'dogs': 'puppy hound boxer husky pooch mutts barks leash fetch whelp corgi snout growl woofs',
    'cats': 'kitty tabby purrs meows catty claws lions tiger pumas ounce feral prowl mouse',
    'insults': 'idiot moron dunce clown loser chump dopes dummy ninny twerp brute snobs boors goons jerks',
    'praise': 'bravo kudos extol honor glory great super noble ideal cheer adore toast hails exalt bless '
              'award prize',
    'sizes': 'large small giant teeny bulky dwarf jumbo broad hefty grand minor major petty obese short '
             'stout titan',
    'shapes': 'cubes cones ovoid ovals round curve angle prism spire helix arced solid',
    'math': 'digit count ratio prime value sigma graph slope angle tenth total minus equal axiom proof cubed '
            'roots logic',
    'numbers': 'three seven eight forty fifty sixty dozen fifth sixth tenth first ninth third zeros',
    'time': 'clock watch hours timer early later dawns dusky night today epoch month years daily dates march '
            'diary',
    'landforms': 'mount ridge cliff mesas butte delta plain gorge dunes bluff knoll islet coast beach crest',
    'religion': 'faith psalm bible deity altar saint pious glory grace abbey friar monks chant pagan rabbi '
                'vicar choir angel',
    'myth': 'titan satyr nymph siren fairy giant gnome troll dryad myths hydra fable ogres elves',
    'medicine': 'nurse medic pills doses heals salve drugs serum cures tonic swabs stent gauze',
    'sickness': 'fever cough virus aches colds chill vomit ulcer croup mumps polio tumor lupus',
    'cooking': 'roast grill broil steam saute toast poach knead whisk slice baste fried boils bakes dices '
               'mince',
    'motion': 'march crawl creep glide hover skate slide swirl swing twirl whirl dance prowl stomp strut '
              'amble lunge',
    'speech': 'speak shout utter voice chant croak quote state spiel yells rants orate opine drawl lisps',
    'sounds': 'noise sound clang crash thump bleep chime whine growl snore click bangs boing creak clunk '
              'knock',
    'smells': 'aroma scent odour smell stink musky fetid musty reeks wafts fumes spicy smoky sniff',
    'textures': 'rough silky shiny bumpy fuzzy furry lumpy sleek slimy waxen hairy satin tacky soggy spiky',
    'light': 'light shine gleam flash flare torch spark glint sunny lucid lamps beams glows prism',
    'fire': 'flame blaze ember smoke torch spark ashes coals fiery burns sears ashen pyres singe scald',
    'cold': 'frost chill snowy sleet gelid nippy polar icily icing brisk bleak numbs',
    'heat': 'humid sweat scald roast fever sunny balmy toast steam muggy baked parch',
    'sleep': 'sleep dream snore sheet duvet awake tired dozes nappy yawns bunks quilt rests',
    'party': 'party dance disco music guest cheer feast toast cakes beers games hosts balls revel favor',
    'wedding': 'bride groom altar usher toast dance waltz rings veils cakes marry union honey tiara',
    'baby': 'nanny potty teeth nappy cribs tummy burps mommy daddy nurse sleep bathe child stork',
    'family': 'niece uncle aunts twins elder bride mommy daddy child clans tribe widow heirs',
    'friends': 'buddy amigo crony amity loyal trust mates chums bonds peers homie unity',
    'travel': 'route guide hotel motel ferry plane coach trips tours visas roams hikes jaunt fares',
    'camping': 'trail cabin lodge torch flame stove canoe kayak scout tents camps hikes tarps woods grill '
               'fires stars',
    'theater': 'stage scene actor drama comic farce opera usher plays roles casts mimes plots wings props '
               'aisle lines',
    'film': 'movie actor scene drama reels shots frame genre plots films stars extra cameo video stunt',
    'writing': 'novel story essay prose verse fable draft write diary quill paper poems pages books plots',
    'art': 'paint brush easel mural chalk image color craft draws inked shade frame gesso model',
    'poetry': 'verse rhyme meter haiku lyric poems poets bards elegy canto iambs muses lines prose',
    'dance': 'tango waltz salsa rumba polka twist disco swing steps mambo conga samba twirl jives limbo '
             'tutus',
    'games': 'chess poker cards bingo darts rummy trump jacks token queen pawns rooks kings board piece '
             'score',
    'toys': 'dolls kites balls block teddy robot train truck games jacks drums bikes skate',
    'circus': 'clown rings tents lions tiger trick hoops stunt magic tamer bears seals cages whips flips',
    'pirates': 'ships sails plank booty loots mates masts chest skull sword patch hooks decks cargo',
    'western': 'ranch rodeo horse lasso posse spurs colts rifle steer boots chaps mesas dusty',
    'medieval': 'lance joust siege tower manor sword armor knave liege serfs friar baron crest',
    'war': 'enemy siege rifle troop fight bombs tanks medal shell truce march blitz drone fleet',
    'politics': 'voter votes party elect polls mayor union rally lobby quota rebel clout state',
    'economy': 'trade price labor wages banks debts loans funds stock booms crash spend money goods',
    'ocean': 'ocean waves tides surfs reefs shore coast beach shell tidal coral swell depth brine',
    'desert': 'sandy dunes oasis camel cacti dried mesas sands parch dusty stark gecko scrub',
    'jungle': 'vines palms tiger snake liana tapir lemur swamp humid leafy mango chimp gecko',
    'arctic': 'polar igloo snowy seals floes husky frost chill sleds icily orcas bears parka',
    'mountains': 'peaks slope ridge cliff climb crags rocky steep scree butte crest gorge mount snowy',
    'rivers': 'river creek brook delta banks canal fjord rapid flows inlet bayou basin mouth levee',
    'city': 'urban towns plaza metro tower block alley civic slums mayor condo cabby malls parks buses',
    'road': 'roads route lanes drive curve merge exits ramps truck speed tolls signs paved',
    'trains': 'train rails track depot coach steam cargo trams metro fares cabin brake',
    'flight': 'plane pilot wings glide hover aloft cargo radar cabin soars flier crash delay gates skies',
    'boats': 'boats yacht canoe kayak ferry barge rafts sloop ketch scull helms decks hulls sails liner',
    'bakery': 'bread bagel scone flour dough yeast crust baker torte icing tarts rolls cakes ovens crumb',
    'candy': 'candy fudge taffy gummy treat sweet sugar cocoa mints lolly chewy icing jelly',
    'dessert': 'cakes torte icing cream sugar sweet fudge crepe tarts jelly flans cocoa scone candy',
    'breakfast': 'bacon toast bagel juice latte syrup crepe scone honey jelly grits fruit cocoa',
    'drinks': 'water juice latte mocha cocoa cider drink sodas shake tonic punch brews',
    'alcohol': 'beers wines cider vodka lager stout booze drunk tipsy pints shots drink toast tonic',
    'dairy': 'dairy cream milky curds swiss moldy rinds aging wheel udder churn goats milks',
    'spices': 'cumin thyme basil clove anise chili curry spice salty tangy zesty spicy sumac herbs mints',
    'vegetables': 'onion beans leeks chard beets kales maize gourd chive cress tuber salad green',
    'fruit': 'apple grape lemon melon mango peach berry guava olive limes plums pears dates kiwis',
    'grains': 'pecan acorn hazel seeds shell nutty grain beans husks wheat maize grits flour',
    'slang': 'dudes savvy gonna wanna gotta sorta kinda dunno nerdy geeky dorky lingo props swank sassy '
             'bling',
    'sadness': 'grief upset weepy gloom blues mopey tears sorry sulky moody bleak dread alone',
    'joy': 'happy merry jolly cheer bliss elate smile laugh grins sunny perky peppy giddy proud',
    'fashion': 'style vogue trend model dress jeans sassy suave swank glitz silky denim linen tweed satin '
               'posed',
    'hair': 'curls braid bangs combs brush perms blond frizz locks tress manes shave razor beard trims salon '
            'bobby',
    'sewing': 'seams spool pleat quilt patch knits yarns looms baste darns sewed tacks laces tulle twine '
              'cloth weave woven',
    'fishing': 'trout perch reels lures hooks baits casts angle catch bream smelt flies float bites trawl',
    'hunting': 'rifle arrow decoy stalk track traps hound scent blind moose tusks games shoot lodge',
}

EMOJI = {'G': '🟩', 'Y': '🟨', 'B': '⬜'}


def theme_puzzles(name, answers, lo=0, hi=5):
    """(colored, clue, pattern, target) for each puzzle whose clue and target are both in theme `name`."""
    answer_set = set(answers)
    words = sorted(w for w in set(THEMES[name].split()) if len(w) == 5)
    targets = {w for w in words if w in answer_set}
    hits = []
    for clue in words:
        buckets = defaultdict(list)
        for t in answers:
            buckets[score(clue, t)].append(t)
        for pat, ts in buckets.items():
            k = 5 - pat.count('B')
            if len(ts) == 1 and ts[0] in targets and ts[0] != clue and lo <= k <= hi:
                hits.append((k, clue, pat, ts[0]))
    return sorted(hits)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('themes', nargs='*', help='themes to search (default: all)')
    ap.add_argument('--min', type=int, default=0, help='min colored boxes')
    ap.add_argument('--max', type=int, default=5, help='max colored boxes')
    ap.add_argument('--list', action='store_true', help='list themes and their words')
    args = ap.parse_args()

    answers = load(Path(__file__).parent / 'data/answers.txt')
    answer_set = set(answers)

    if args.list:
        for name, words in THEMES.items():
            ws = sorted(set(words.split()))
            targets = [w for w in ws if w in answer_set]
            print(f"{name}: {len(ws)} words, {len(targets)} usable as targets\n  {' '.join(ws)}")
        raise SystemExit

    for name in args.themes or THEMES:
        if name not in THEMES:
            print(f"unknown theme {name!r}; try --list\n")
            continue
        hits = theme_puzzles(name, answers, args.min, args.max)
        print(f"{name}: {len(hits)} puzzle(s)")
        for k, clue, pat, t in hits:
            print(f"  {clue.upper()}  {''.join(EMOJI[c] for c in pat)}  →  {t.upper()}   ({k} colored)")
        print()
