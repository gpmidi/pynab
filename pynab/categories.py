import regex
import collections
from pynab import log

# category codes
# these are stored in the db, as well
CAT_GAME_NDS = 1010
CAT_GAME_PSP = 1020
CAT_GAME_WII = 1030
CAT_GAME_XBOX = 1040
CAT_GAME_XBOX360 = 1050
CAT_GAME_WIIWARE = 1060
CAT_GAME_XBOX360DLC = 1070
CAT_GAME_PS3 = 1080
CAT_MOVIE_FOREIGN = 2010
CAT_MOVIE_OTHER = 2020
CAT_MOVIE_SD = 2030
CAT_MOVIE_HD = 2040
CAT_MOVIE_BLURAY = 2050
CAT_MOVIE_3D = 2060
CAT_MUSIC_MP3 = 3010
CAT_MUSIC_VIDEO = 3020
CAT_MUSIC_AUDIOBOOK = 3030
CAT_MUSIC_LOSSLESS = 3040
CAT_PC_0DAY = 4010
CAT_PC_ISO = 4020
CAT_PC_MAC = 4030
CAT_PC_MOBILEOTHER = 4040
CAT_PC_GAMES = 4050
CAT_PC_MOBILEIOS = 4060
CAT_PC_MOBILEANDROID = 4070
CAT_TV_FOREIGN = 5020
CAT_TV_SD = 5030
CAT_TV_HD = 5040
CAT_TV_OTHER = 5050
CAT_TV_SPORT = 5060
CAT_TV_ANIME = 5070
CAT_TV_DOCU = 5080
CAT_XXX_DVD = 6010
CAT_XXX_WMV = 6020
CAT_XXX_XVID = 6030
CAT_XXX_X264 = 6040
CAT_XXX_PACK = 6050
CAT_XXX_IMAGESET = 6060
CAT_XXX_OTHER = 6070
CAT_BOOK_MAGS = 7010
CAT_BOOK_EBOOK = 7020
CAT_BOOK_COMICS = 7030

CAT_MISC_OTHER = 8010

CAT_PARENT_GAME = 1000
CAT_PARENT_MOVIE = 2000
CAT_PARENT_MUSIC = 3000
CAT_PARENT_PC = 4000
CAT_PARENT_TV = 5000
CAT_PARENT_XXX = 6000
CAT_PARENT_BOOK = 7000
CAT_PARENT_MISC = 8000

"""
This dict maps groups to potential categories. Some groups tend
to favour some release types over others, so you can specify those
here. If none of the suggestions for that group match, it'll just
try all possible categories. Categories are listed in order of priority.

There are two options for the list: either a parent category, or a subcategory.
If a parent category is supplied, the release will be checked against every
sub-category. If a subcategory is supplied, the release will automatically
be categorised as that.

ie.
[CAT_PARENT_PC, CAT_PC_0DAY]

Will attempt to categorise the release by every subcategory of PC. If no
match is found, it'll tag it as PC_0DAY.

You can also just leave it with only parent categories, in which case
the algorithm will fall through to attempting every single subcat (or failing).
A release is only categorised here on no-match if the array ends on a subcategory.
"""
group_regex = {
    regex.compile('alt\.binaries\.0day', regex.I): [
        CAT_PARENT_PC, CAT_PC_0DAY
    ],
    regex.compile('alt\.binaries\.ath', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_GAME, CAT_PARENT_PC, CAT_PARENT_TV, CAT_PARENT_MOVIE, CAT_PARENT_MUSIC,
        CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.b4e', regex.I): [
        CAT_PARENT_PC, CAT_PARENT_BOOK
    ],
    regex.compile('alt\.binaries\..*?audiobook.*?', regex.I): [
        CAT_MUSIC_AUDIOBOOK
    ],
    regex.compile('lossless|flac', regex.I): [
        CAT_MUSIC_LOSSLESS
    ],
    regex.compile('alt\.binaries\.sounds.*?|alt\.binaries\.mp3.*?|alt\.binaries.*?\.mp3', regex.I): [
        CAT_PARENT_MUSIC, CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.console.ps3', regex.I): [
        CAT_PARENT_GAME, CAT_GAME_PS3
    ],
    regex.compile('alt\.binaries\.games\.xbox*', regex.I): [
        CAT_PARENT_GAME, CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE
    ],
    regex.compile('alt\.binaries\.games$', regex.I): [
        CAT_PARENT_GAME, CAT_PC_GAMES
    ],
    regex.compile('alt\.binaries\.games\.wii', regex.I): [
        CAT_PARENT_GAME
    ],
    regex.compile('alt\.binaries\.dvd.*?', regex.I): [
        CAT_PARENT_BOOK, CAT_PARENT_PC, CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE
    ],
    regex.compile('alt\.binaries\.hdtv*|alt\.binaries\.x264|alt\.binaries\.tv$', regex.I): [
        CAT_PARENT_MUSIC, CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE
    ],
    regex.compile('alt\.binaries\.nospam\.cheerleaders', regex.I): [
        CAT_PARENT_MUSIC, CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_PC, CAT_PARENT_MOVIE
    ],
    regex.compile('alt\.binaries\.classic\.tv.*?', regex.I): [
        CAT_PARENT_TV, CAT_TV_OTHER
    ],
    regex.compile('alt\.binaries\.multimedia', regex.I): [
        CAT_PARENT_MOVIE, CAT_PARENT_TV
    ],
    regex.compile('alt\.binaries\.multimedia\.anime(\.highspeed)?', regex.I): [
        CAT_TV_ANIME
    ],
    regex.compile('alt\.binaries\.anime', regex.I): [
        CAT_TV_ANIME
    ],
    regex.compile('alt\.binaries\.e(-|)book*?', regex.I): [
        CAT_PARENT_BOOK, CAT_BOOK_EBOOK
    ],
    regex.compile('alt\.binaries\.comics.*?', regex.I): [
        CAT_BOOK_COMICS
    ],
    regex.compile('alt\.binaries\.cores.*?', regex.I): [
        CAT_PARENT_BOOK, CAT_PARENT_XXX, CAT_PARENT_GAME, CAT_PARENT_PC, CAT_PARENT_MUSIC, CAT_PARENT_TV,
        CAT_PARENT_MOVIE, CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.lou', regex.I): [
        CAT_PARENT_BOOK, CAT_PARENT_XXX, CAT_PARENT_GAME, CAT_PARENT_PC, CAT_PARENT_TV, CAT_PARENT_MOVIE,
        CAT_PARENT_MUSIC, CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.cd.image|alt\.binaries\.audio\.warez', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_PC, CAT_PC_0DAY
    ],
    regex.compile('alt\.binaries\.pro\-wrestling', regex.I): [
        CAT_TV_SPORT
    ],
    regex.compile('alt\.binaries\.sony\.psp', regex.I): [
        CAT_GAME_PSP
    ],
    regex.compile('alt\.binaries\.nintendo\.ds|alt\.binaries\.games\.nintendods', regex.I): [
        CAT_GAME_NDS
    ],
    regex.compile('alt\.binaries\.mpeg\.video\.music', regex.I): [
        CAT_MUSIC_VIDEO
    ],
    regex.compile('alt\.binaries\.mac', regex.I): [
        CAT_PC_MAC
    ],
    regex.compile('linux', regex.I): [
        CAT_PC_ISO
    ],
    regex.compile('alt\.binaries\.illuminaten', regex.I): [
        CAT_PARENT_PC, CAT_PARENT_XXX, CAT_PARENT_MUSIC, CAT_PARENT_GAME, CAT_PARENT_TV, CAT_PARENT_MOVIE,
        CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.ipod\.videos\.tvshows', regex.I): [
        CAT_TV_OTHER
    ],
    regex.compile('alt\.binaries\.documentaries', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE, CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.drummers', regex.I): [
        CAT_PARENT_BOOK, CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE
    ],
    regex.compile('alt\.binaries\.tv\.swedish', regex.I): [
        CAT_TV_FOREIGN
    ],
    regex.compile('alt\.binaries\.tv\.deutsch', regex.I): [
        CAT_TV_FOREIGN
    ],
    regex.compile('alt\.binaries\.erotica\.divx', regex.I): [
        CAT_PARENT_XXX, CAT_XXX_OTHER
    ],
    regex.compile('alt\.binaries\.ghosts', regex.I): [
        CAT_PARENT_BOOK, CAT_PARENT_XXX, CAT_PARENT_PC, CAT_PARENT_MUSIC, CAT_PARENT_GAME, CAT_PARENT_TV,
        CAT_PARENT_MOVIE
    ],
    regex.compile('alt\.binaries\.mom', regex.I): [
        CAT_PARENT_BOOK, CAT_PARENT_XXX, CAT_PARENT_PC, CAT_PARENT_MUSIC, CAT_PARENT_GAME, CAT_PARENT_TV,
        CAT_PARENT_MOVIE, CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.mma|alt\.binaries\.multimedia\.sports.*?', regex.I): [
        CAT_TV_SPORT
    ],
    regex.compile('alt\.binaries\.b4e$', regex.I): [
        CAT_PARENT_PC
    ],
    regex.compile('alt\.binaries\.warez\.smartphone', regex.I): [
        CAT_PARENT_PC
    ],
    regex.compile('alt\.binaries\.warez\.ibm\-pc\.0\-day|alt\.binaries\.warez', regex.I): [
        CAT_PARENT_GAME, CAT_PARENT_BOOK, CAT_PARENT_XXX, CAT_PARENT_MUSIC, CAT_PARENT_PC, CAT_PARENT_TV,
        CAT_PARENT_MOVIE, CAT_PC_0DAY
    ],
    regex.compile('erotica|ijsklontje|kleverig', regex.I): [
        CAT_PARENT_XXX, CAT_XXX_OTHER
    ],
    regex.compile('french', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_TV, CAT_MOVIE_FOREIGN
    ],
    regex.compile('alt\.binaries\.movies\.xvid|alt\.binaries\.movies\.divx|alt\.binaries\.movies', regex.I): [
        CAT_PARENT_BOOK, CAT_PARENT_GAME, CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE, CAT_PARENT_PC, CAT_MISC_OTHER
    ],
    regex.compile('wmvhd', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE
    ],
    regex.compile('inner\-sanctum', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_PC, CAT_PARENT_BOOK, CAT_PARENT_MUSIC, CAT_PARENT_TV, CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.worms', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MUSIC, CAT_PARENT_MOVIE
    ],
    regex.compile('alt\.binaries\.x264', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_TV, CAT_PARENT_MOVIE, CAT_MOVIE_OTHER
    ],
    regex.compile('dk\.binaer\.ebooks', regex.I): [
        CAT_PARENT_BOOK, CAT_BOOK_EBOOK
    ],
    regex.compile('dk\.binaer\.film', regex.I): [
        CAT_PARENT_TV, CAT_PARENT_MOVIE, CAT_MISC_OTHER
    ],
    regex.compile('dk\.binaer\.musik', regex.I): [
        CAT_PARENT_MUSIC, CAT_MISC_OTHER
    ],
    regex.compile('alt\.binaries\.(teevee|multimedia|tv|tvseries).*?', regex.I): [
        CAT_PARENT_XXX, CAT_PARENT_GAME, CAT_PARENT_MUSIC, CAT_PARENT_TV, CAT_PARENT_PC, CAT_PARENT_MOVIE,
        CAT_MISC_OTHER
    ],
}

"""
This dict holds parent categories, initial regexes and potential actions.

Dict is called in parts (ie. just the. CAT_PARENT_TV section)
In order, the library will try to match the release name against
each parent regex - on success, it will proceed to execute individual
category regex in the order supplied. If there's no match, it'll try the
next parent regex - if none match, the function will return False. This
means that the next category suggested by the group will be tried.

Note that if the array ends on an OTHER subcategory (ie. a category not listed
in category_regex), it'll automatically tag the release as that.

As an example, we attempt to match the release to every type of movie
before failing through to CAT_MOVIE_OTHER if 'xvid' is in the title. In
that example, if it matches no category and doesn't have xvid in the title,
it'll be returned to whatever called it for further processing.
"""
parent_category_regex = {
    CAT_PARENT_TV: collections.OrderedDict([
        (regex.compile('(S?(\d{1,2})\.?(E|X|D)(\d{1,2})[\. _-]+)|(dsr|pdtv|hdtv)[\.\-_]', regex.I), [
            CAT_TV_FOREIGN, CAT_TV_SPORT, CAT_TV_DOCU, CAT_TV_HD, CAT_TV_SD, CAT_TV_OTHER
        ]),
        (regex.compile(
            '( S\d{1,2} |\.S\d{2}\.|\.S\d{2}|s\d{1,2}e\d{1,2}|(\.| |\b|\-)EP\d{1,2}\.|\.E\d{1,2}\.|special.*?HDTV|HDTV.*?special|PDTV|\.\d{3}\.DVDrip|History( |\.|\-)Channel|trollhd|trollsd|HDTV.*?BTL|C4TV|WEB DL|web\.dl|WWE|season \d{1,2}|(?!collectors).*?series|\.TV\.|\.dtv\.|UFC|TNA|staffel|episode|special\.\d{4})',
            regex.I), [
             CAT_TV_FOREIGN, CAT_TV_SPORT, CAT_TV_DOCU, CAT_TV_HD, CAT_TV_SD, CAT_TV_OTHER
         ]),
        (regex.compile('seizoen', regex.I), [
            CAT_TV_FOREIGN
        ])
    ]),
    CAT_PARENT_MOVIE: collections.OrderedDict([
        (regex.compile('', regex.I), [
            CAT_MOVIE_FOREIGN, CAT_MOVIE_SD, CAT_MOVIE_3D, CAT_MOVIE_HD, CAT_MOVIE_BLURAY
        ]),
        (regex.compile('xvid', regex.I), [
            CAT_MOVIE_OTHER
        ])
    ]),
    CAT_PARENT_PC: collections.OrderedDict([
        (regex.compile('', regex.I), [
            CAT_PC_MOBILEANDROID, CAT_PC_MOBILEIOS, CAT_PC_MOBILEOTHER, CAT_PC_ISO, CAT_PC_MAC, CAT_PC_GAMES,
            CAT_PC_0DAY
        ])
    ]),
    CAT_PARENT_XXX: collections.OrderedDict([
        (regex.compile(
            '(\.JAV\.| JAV |\.Jav\.|Girls.*?Gone.*?Wild|\-MotTto|-Nukleotide|XXX|PORNOLATiON|SWE6RUS|swe6|SWE6|NYMPHO|DETOXATiON|DivXfacTory|TESORO|STARLETS|xxx|XxX|PORNORIP|PornoRip)',
            regex.I), [
             CAT_XXX_DVD, CAT_XXX_IMAGESET, CAT_XXX_PACK, CAT_XXX_WMV, CAT_XXX_X264, CAT_XXX_XVID, CAT_XXX_OTHER
         ]),
        (regex.compile('^Penthouse', regex.I), [
            CAT_XXX_DVD, CAT_XXX_IMAGESET, CAT_XXX_PACK, CAT_XXX_WMV, CAT_XXX_X264, CAT_XXX_XVID, CAT_XXX_OTHER
        ])
    ]),
    CAT_PARENT_GAME: collections.OrderedDict([
        (regex.compile('', regex.I), [
            CAT_GAME_NDS, CAT_GAME_PS3, CAT_GAME_PSP, CAT_GAME_WIIWARE, CAT_GAME_WIIWARE, CAT_GAME_XBOX360DLC,
            CAT_GAME_XBOX360, CAT_GAME_XBOX
        ])
    ]),
    CAT_PARENT_MUSIC: collections.OrderedDict([
        (regex.compile('', regex.I), [
            CAT_MUSIC_VIDEO, CAT_MUSIC_LOSSLESS, CAT_MUSIC_AUDIOBOOK, CAT_MUSIC_MP3
        ])
    ]),
    CAT_PARENT_BOOK: collections.OrderedDict([
        (regex.compile('', regex.I), [
            CAT_BOOK_COMICS, CAT_BOOK_MAGS, CAT_BOOK_EBOOK
        ])
    ])
}

"""
This contains acceptable regex for each category. Again, it's called in
chunks - one category at a time. Functions will attempt each regex (in
order) until it matches (and returns that category) or fails.

Each element in the array can be three things:
- a Dict
- a Tuple
- or anything else (generally a compiled regex pattern)

--Dicts--
CAT_MOVIE_3D: [
    {
        regex.compile('3D', regex.I): True,
        regex.compile('[\-\. _](H?SBS|OU)([\-\. _]|$)', regex.I): True
    }
]
The dict signifies that both regexes must match their supplied values
for the category to be applied. In this case, both regexes must match.
If we wanted one to match and one to not, we'd mark one as False.

--Lists--
(regex.compile('DVDRIP|XVID.*?AC3|DIVX\-GERMAN', regex.I), False)
In this example, we set the category to fail if the regex matches.
Consider it as: (regex, categorise?)

--Patterns--
CAT_TV_HD: [
    regex.compile('1080|720', regex.I)
],
The majority of entries look like this: match this release to this category
if this regex matches.
"""
category_regex = {
    CAT_TV_FOREIGN: [
        regex.compile(
            '(seizoen|staffel|danish|flemish|(\.| |\b|\-)(HU|NZ)|dutch|Deutsch|nl\.?subbed|nl\.?sub|\.NL|\.ITA|norwegian|swedish|swesub|french|german|spanish)[\.\- \b]',
            regex.I),
        regex.compile(
            '\.des\.(?!moines)|Chinese\.Subbed|vostfr|Hebrew\.Dubbed|\.HEB\.|Nordic|Hebdub|NLSubs|NL\-Subs|NLSub|Deutsch| der |German | NL |staffel|videomann',
            regex.I),
        regex.compile(
            '(danish|flemish|nlvlaams|dutch|nl\.?sub|swedish|swesub|icelandic|finnish|french|truefrench[\.\- ](?:.dtv|dvd|br|bluray|720p|1080p|LD|dvdrip|internal|r5|bdrip|sub|cd\d|dts|dvdr)|german|nl\.?subbed|deutsch|espanol|SLOSiNH|VOSTFR|norwegian|[\.\- ]pl|pldub|norsub|[\.\- ]ITA)[\.\- ]',
            regex.I),
        regex.compile('(french|german)$', regex.I)
    ],
    CAT_TV_SPORT: [
        regex.compile(
            '(f1\.legends|epl|motogp|bellator|strikeforce|the\.ultimate\.fighter|supercup|wtcc|red\.bull.*?race|tour\.de\.france|bundesliga|la\.liga|uefa|EPL|ESPN|WWE\.|WWF\.|WCW\.|MMA\.|UFC\.|(^|[\. ])FIA\.|PGA\.|NFL\.|NCAA\.)',
            regex.I),
        regex.compile(
            'Twenty20|IIHF|wimbledon|Kentucky\.Derby|WBA|Rugby\.|TNA\.|DTM\.|NASCAR|SBK|NBA(\.| )|NHL\.|NRL\.|MLB\.|Playoffs|FIFA\.|Serie.A|netball\.anz|formula1|indycar|Superleague|V8\.Supercars|((19|20)\d{2}.*?olympics?|olympics?.*?(19|20)\d{2})|x(\ |\.|\-)games',
            regex.I),
        regex.compile(
            '(\b|\_|\.| )(Daegu|AFL|La.Vuelta|BMX|Gymnastics|IIHF|NBL|FINA|Drag.Boat|HDNET.Fights|Horse.Racing|WWF|World.Championships|Tor.De.France|Le.Triomphe|Legends.Of.Wrestling)(\b|\_|\.| )',
            regex.I),
        regex.compile(
            '(\b|\_|\.| )(Fighting.Championship|tour.de.france|Boxing|Cycling|world.series|Formula.Renault|FA.Cup|WRC|GP3|WCW|Road.Racing|AMA|MFC|Grand.Prix|Basketball|MLS|Wrestling|World.Cup)(\b|\_|\.| )',
            regex.I),
        regex.compile(
            '(\b|\_|\.| )(Swimming.*?Men|Swimming.*?Women|swimming.*?champion|WEC|World.GP|CFB|Rally.Challenge|Golf|Supercross|WCK|Darts|SPL|Snooker|League Cup|Ligue1|Ligue)(\b|\_|\.| )',
            regex.I),
        regex.compile(
            '(\b|\_|\.| )(Copa.del.rey|League.Cup|Carling.Cup|Cricket|The.Championship|World.Max|KNVB|GP2|Soccer|PGR3|Cage.Contender|US.Open|CFL|Weightlifting|New.Delhi|Euro|WBC)(\b|\_|\.| )',
            regex.I),
        regex.compile('^london(\.| )2012', regex.I)
    ],
    CAT_TV_DOCU: [
        (regex.compile('\-DOCUMENT', regex.I), False),
        regex.compile(
            '(?!.*?S\d{2}.*?)(?!.*?EP?\d{2}.*?)(48\.Hours\.Mystery|Discovery.Channel|BBC|History.Channel|National.Geographic|Nat Geo|Shark.Week)',
            regex.I),
        regex.compile(
            '(?!.*?S\d{2}.*?)(?!.*?EP?\d{2}.*?)((\b|_)(docu|BBC|document|a.and.e|National.geographic|Discovery.Channel|History.Channel|Travel.Channel|Science.Channel|Biography|Modern.Marvels|Inside.story|Hollywood.story|E.True|Documentary)(\b|_))',
            regex.I),
        regex.compile(
            '(?!.*?S\d{2}.*?)(?!.*?EP?\d{2}.*?)((\b|_)(Science.Channel|National.geographi|History.Chanel|Colossal|Discovery.travel|Planet.Science|Animal.Planet|Discovery.Sci|Regents|Discovery.World|Discovery.truth|Discovery.body|Dispatches|Biography|The.Investigator|Private.Life|Footballs.Greatest|Most.Terrifying)(\b|_))',
            regex.I)
    ],
    CAT_TV_HD: [
        regex.compile('1080|720', regex.I)
    ],
    CAT_TV_SD: [
        regex.compile('(SDTV|HDTV|XVID|DIVX|PDTV|WEBDL|DVDR|DVD-RIP|WEB-DL|x264|dvd)', regex.I)
    ],
    CAT_MOVIE_FOREIGN: [
        regex.compile(
            '(\.des\.|danish|flemish|dutch|(\.| |\b|\-)(HU|FINA)|Deutsch|nl\.?subbed|nl\.?sub|\.NL|\.ITA|norwegian|swedish|swesub|french|german|spanish)[\.\- |\b]',
            regex.I),
        regex.compile(
            'Chinese\.Subbed|vostfr|Hebrew\.Dubbed|\.Heb\.|Hebdub|NLSubs|NL\-Subs|NLSub|Deutsch| der |German| NL |turkish',
            regex.I),
        regex.compile(
            '(danish|flemish|nlvlaams|dutch|nl\.?sub|swedish|swesub|icelandic|finnish|french|truefrench[\.\- ](?:dvd|br|bluray|720p|1080p|LD|dvdrip|internal|r5|bdrip|sub|cd\d|dts|dvdr)|german|nl\.?subbed|deutsch|espanol|SLOSiNH|VOSTFR|norwegian|[\.\- ]pl|pldub|norsub|[\.\- ]ITA)[\.\- ]',
            regex.I)
    ],
    CAT_MOVIE_SD: [
        regex.compile('(dvdscr|extrascene|dvdrip|\.CAM|dvdr|dvd9|dvd5|[\.\-\ ]ts)[\.\-\ ]', regex.I),
        {
            regex.compile('(divx|xvid|(\.| )r5(\.| ))', regex.I): True,
            regex.compile('(720|1080)', regex.I): False,
        }
    ],
    CAT_MOVIE_3D: [
        {
            regex.compile('3D', regex.I): True,
            regex.compile('[\-\. _](H?SBS|OU)([\-\. _]|$)', regex.I): True
        }
    ],
    CAT_MOVIE_HD: [
        regex.compile('x264|wmvhd|web\-dl|XvidHD|BRRIP|HDRIP|HDDVD|bddvd|BDRIP|webscr', regex.I)
    ],
    CAT_MOVIE_BLURAY: [
        regex.compile('bluray|bd?25|bd?50|blu-ray|VC1|VC\-1|AVC|BDREMUX', regex.I)
    ],
    CAT_PC_MOBILEANDROID: [
        regex.compile('Android', regex.I)
    ],
    CAT_PC_MOBILEIOS: [
        regex.compile('(?!.*?Winall.*?)(IPHONE|ITOUCH|IPAD|Ipod)', regex.I)
    ],
    CAT_PC_MOBILEOTHER: [
        regex.compile('COREPDA|symbian|xscale|wm5|wm6|J2ME', regex.I)
    ],
    CAT_PC_0DAY: [
        (regex.compile('DVDRIP|XVID.*?AC3|DIVX\-GERMAN', regex.I), False),
        regex.compile(
            '[\.\-_ ](x32|x64|x86|win64|winnt|win9x|win2k|winxp|winnt2k2003serv|win9xnt|win9xme|winnt2kxp|win2kxp|win2kxp2k3|keygen|regged|keymaker|winall|win32|template|Patch|GAMEGUiDE|unix|irix|solaris|freebsd|hpux|linux|windows|multilingual|software|Pro v\d{1,3})[\.\-_ ]',
            regex.I),
        regex.compile(
            '(?!MDVDR).*?\-Walmart|PHP|\-SUNiSO|\.Portable\.|Adobe|CYGNUS|GERMAN\-|v\d{1,3}.*?Pro|MULTiLANGUAGE|Cracked|lz0|\-BEAN|MultiOS|\-iNViSiBLE|\-SPYRAL|WinAll|Keymaker|Keygen|Lynda\.com|FOSI|Keyfilemaker|DIGERATI|\-UNION|\-DOA|Laxity',
            regex.I)
    ],
    CAT_PC_MAC: [
        regex.compile('osx|os\.x|\.mac\.|MacOSX', regex.I)
    ],
    CAT_PC_ISO: [
        regex.compile('\-DYNAMiCS', regex.I)
    ],
    CAT_PC_GAMES: [
        regex.compile('\-Heist|\-RELOADED|\.GAME\-|\-SKIDROW|PC GAME|FASDOX|v\d{1,3}.*?\-TE|RIP\-unleashed|Razor1911',
                   regex.I)
    ],
    CAT_XXX_X264: [
        regex.compile('x264|720|1080', regex.I)
    ],
    CAT_XXX_XVID: [
        regex.compile('xvid|dvdrip|bdrip|brrip|pornolation|swe6|nympho|detoxication|tesoro|mp4', regex.I)
    ],
    CAT_XXX_WMV: [
        regex.compile('wmv|f4v|flv|mov(?!ie)|mpeg|isom|realmedia|multiformat', regex.I)
    ],
    CAT_XXX_DVD: [
        regex.compile('dvdr[^ip]|dvd5|dvd9', regex.I)
    ],
    CAT_XXX_PACK: [
        regex.compile('[\._](pack)[\.\-_]', regex.I)
    ],
    CAT_XXX_IMAGESET: [
        regex.compile('imageset', regex.I)
    ],
    CAT_GAME_NDS: [
        regex.compile('(\b|\-| |\.)(3DS|NDS)(\b|\-| |\.)', regex.I)
    ],
    CAT_GAME_PS3: [
        regex.compile('PS3\-', regex.I)
    ],
    CAT_GAME_PSP: [
        regex.compile('PSP\-', regex.I)
    ],
    CAT_GAME_WIIWARE: [
        regex.compile('WIIWARE|WII.*?VC|VC.*?WII|WII.*?DLC|DLC.*?WII|WII.*?CONSOLE|CONSOLE.*?WII', regex.I)
    ],
    CAT_GAME_WII: [
        (regex.compile('WWII.*?(?!WII)', regex.I), False),
        regex.compile('Wii', regex.I)
    ],
    CAT_GAME_XBOX360DLC: [
        regex.compile('(DLC.*?xbox360|xbox360.*?DLC|XBLA.*?xbox360|xbox360.*?XBLA)', regex.I)
    ],
    CAT_GAME_XBOX360: [
        regex.compile('XBOX360|x360', regex.I)
    ],
    CAT_GAME_XBOX: [
        regex.compile('XBOX', regex.I)
    ],
    CAT_MUSIC_VIDEO: [
        (regex.compile('(HDTV|S\d{1,2}|\-1920)', regex.I), False),
        regex.compile(
            '\-DDC\-|mbluray|\-VFI|m4vu|retail.*?(?!bluray.*?)x264|\-assass1ns|\-uva|(?!HDTV).*?\-SRP|x264.*?Fray|JESTERS|iuF|MDVDR|(?!HDTV).*?\-BTL|\-WMVA|\-GRMV|\-iLUV|x264\-(19|20)\d{2}',
            regex.I)
    ],
    CAT_MUSIC_AUDIOBOOK: [
        regex.compile('(audiobook|\bABOOK\b)', regex.I)
    ],
    CAT_MUSIC_MP3: [
        (regex.compile('dvdrip|xvid|(x|h)264|720p|1080(i|p)|Bluray', regex.I), False),
        regex.compile(
            '( |\_)Int$|\-(19|20)\d{2}\-[a-z0-9]+$|^V A |Top.*?Charts|Promo CDS|Greatest(\_| )Hits|VBR|NMR|CDM|WEB(STREAM|MP3)|\-DVBC\-|\-CD\-|\-CDR\-|\-TAPE\-|\-Live\-\d{4}|\-DAB\-|\-LINE\-|CDDA|-Bootleg-|WEB\-\d{4}|\-CD\-|(\-|)EP\-|\-FM\-|2cd|\-Vinyl\-|\-SAT\-|\-LP\-|\-DE\-|\-cable\-|Radio\-\d{4}|Radio.*?Live\-\d{4}|\-SBD\-|\d{1,3}(CD|TAPE)',
            regex.I),
        regex.compile('^VA(\-|\_|\ )', regex.I)
    ],
    CAT_MUSIC_LOSSLESS: [
        (regex.compile('dvdrip|xvid|264|720p|1080|Bluray', regex.I), False),
        regex.compile('Lossless|FLAC', regex.I)
    ],
    CAT_BOOK_COMICS: [
        regex.compile('cbr|cbz', regex.I)
    ],
    CAT_BOOK_MAGS: [
        regex.compile('Mag(s|azin|azine|azines)', regex.I)
    ],
    CAT_BOOK_EBOOK: [
        regex.compile('^(.* - (?:\[.*\] -)? .* (?:\[.*\])? \(\w{3,4}\))', regex.I),
        regex.compile('Ebook|E?\-book|\) WW|\[Springer\]| epub|ISBN', regex.I),
        regex.compile('[\(\[](?:(?:html|epub|pdf|mobi|azw|doc).?)+[\)\]]', regex.I)
    ]
}


def determine_category(name, group_name=''):
    """Categorise release based on release name and group name."""
    log.debug('Attempting to determine category for {0}...'.format(name))

    if is_hashed(name):
        log.debug('Release is hashed!')
        return CAT_MISC_OTHER

    category = check_group_category(name, group_name)
    if category:
        return category

    for parent_category in parent_category_regex.keys():
        category = check_parent_category(name, parent_category)
        if category:
            log.debug('Category found as: {:d}'.format(category))
            return category

    # if all else fails
    return CAT_MISC_OTHER


def is_hashed(name):
    """Check if the release name is a hash."""
    return not regex.match('( |\.|\-)', name, regex.I) and regex.match('^[a-f0-9]{16,}$', name, regex.I)


def check_group_category(name, group_name):
    """Check the group name against our list and
    take appropriate action - match against categories
    as dictated in the dicts above."""
    for regex, actions in group_regex.items():
        if regex.search(group_name):
            log.debug('Matched group regex {0}...'.format(regex.pattern))
            for action in actions:
                if action in parent_category_regex.keys():
                    category = check_parent_category(name, action)
                    if category:
                        log.debug('Found category: {:d}!'.format(category))
                        return category
                elif action in category_regex.keys():
                    log.debug('Reached end of list with a single cat {:d}...'.format(action))
                    return action


def check_parent_category(name, parent_category):
    """Check the release against a single parent category, which will
    call appropriate sub-category checks."""
    log.debug('Checking parent category: {:d}'.format(parent_category))

    for test, actions in parent_category_regex[parent_category].items():
        log.debug('Checking parent test (this might be blank): {0}'.format(test.pattern))

        if test.search(name):
            for category in actions:
                if category in category_regex:
                    if check_single_category(name, category):
                        return category
                else:
                    log.debug('Category has no regex tests, assigning: {:d}'.format(category))
                    return category

    return False


def check_single_category(name, category):
    """Check release against a single category."""
    log.debug('Checking single category {0}...'.format(category))

    for regex in category_regex[category]:
        if isinstance(regex, collections.Mapping):
            if all(bool(expr.search(name)) == expected for expr, expected in regex.items()):
                return True
        elif isinstance(regex, tuple):
            (r, ret) = regex
            if r.search(name):
                return ret
        else:
            if regex.search(name):
                return True
    return False