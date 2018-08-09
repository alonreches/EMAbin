###################################################################################
# this file runs the code. it allows to run a single search with a single heuristic
# or run a full test that writes results to a tsv file
###################################################################################
from optparse import OptionParser
from improved_wikipedia import wikipedia
import random
import itertools
from WikiSolver import *
import multiprocessing as mp
import time
import string
import sys

printable = set(string.printable)
TIMEOUT = 60 * 5
POPULAR_PAGES_ID = "37397829"
from sys import argv

DEBUG = False
if len(argv) > 1 and argv[-1] == "debug":
    DEBUG = True


def generate_popular_pages():
    popular_pages = wikipedia.page(pageid=POPULAR_PAGES_ID)
    popular_links = popular_pages.links
    # Generate all possible non-repeating pairs
    pairs = list(itertools.combinations(popular_links, 2))
    # print(popular_pages.title)
    while True:
        # Randomly choose pair of links
        yield random.choice(pairs)


def generate_mergers():
    merger_pages = ['Lortel Archives', 'Allgemeine Deutsche Biographie', 'Glove (ice hockey)',
                    'Australian Plant Name Index', 'Jֳ³zef Razowski', 'Wiley-Blackwell', 'Mississippi Alluvial Plain',
                    'Structurae', 'Lists of Korean films', 'Lists of Indian Punjabi films', 'Groundbreaking',
                    'SAGE Publications', 'RPGA', 'All About Jazz', 'Light characteristic', 'CODEN',
                    'List of Sri Lankan Tamil films', 'Satellite Catalog Number', 'European Community number',
                    'Lists of Sri Lankan films', 'BC Geographical Names', 'Floor area (building)',
                    'Manufacturer\'s empty weight', 'International Designator', 'Dictionary of Canadian Biography',
                    'Verbandsgemeinde', '20-yard shuttle', 'Vertical jump', 'Rediff.com', 'Goals against average',
                    'Centre de donnֳ©es astronomiques de Strasbourg', 'Ships of the Royal Navy', 'J. J. Colledge',
                    'IndieWire', 'Fellow of the Royal Society of Edinburgh', 'Union councils of Pakistan',
                    'Biographical Directory of Federal Judges', 'Balinese saka calendar', 'Classic hits',
                    'Drowned in Sound', 'Games played', 'HanCinema', 'Diseases Database',
                    'Smithsonian Astrophysical Observatory Star Catalog', 'Keel laying', 'Curb weight', 'KulturNav',
                    'Acoustic music', 'Observation arc', 'Norsk biografisk leksikon', 'Dieter Nohlen',
                    '1991 Nepal census', 'Advisory Committee on Antarctic Names', 'Channel (broadcasting)',
                    'Games behind', 'Base Lֳ©onore', 'Bundesverband Musikindustrie', 'Digital Himalaya',
                    'JPL Small-Body Database', 'Normal route', 'Australian Dictionary of Biography',
                    'Stephen Thomas Erlewine', 'BacDive', 'List of ICD-9 codes', 'Aviation Safety Network',
                    'New International Encyclopedia', 'AFI Catalog of Feature Films', 'Inflow (hydrology)',
                    'Fussballdaten.de', 'Specific name (zoology)', 'Forward (ice hockey)', 'Russian Census (2010)',
                    'Full-time equivalent', 'National Register Information System', 'PRIAM enzyme-specific profiles',
                    'IntEnz', 'MetaCyc', 'CiNii', 'Borough (Pennsylvania)', 'Stephan von Breuning (entomologist)',
                    'Turkish Statistical Institute', 'Rec.Sport.Soccer Statistics Foundation', 'Enzyme activator',
                    'Killed in action', 'IUPAC nomenclature of chemistry', 'Mammal Species of the World', 'FloraBase',
                    'Unique Ingredient Identifier', 'Store norske leksikon', 'Historical Dictionary of Switzerland',
                    'Captain (sports)', 'Assist (ice hockey)', 'World Spider Catalog', 'Point (ice hockey)',
                    'Flora of North America', 'Doctoral advisor', 'Internet Broadway Database',
                    'Human Genome Organisation', 'MycoBank', 'Istituto Centrale per il Catalogo Unico',
                    'Parent company', 'Facility ID', 'World Checklist of Selected Plant Families', 'Fossilworks',
                    'Fauna Europaea', 'AllMovie', 'National Biodiversity Network',
                    'Germplasm Resources Information Network', 'Sports Reference', 'BugGuide', 'LIBRIS', 'Bibcode',
                    'Union List of Artist Names', 'Population without double counting', 'Plants of the World Online',
                    'Tropicos', 'GEOnet Names Server', 'World Register of Marine Species',
                    'The Global Lepidoptera Names Index', 'Geographic Names Information System', 'SNAC',
                    'Systֳ¨me universitaire de documentation', 'Global Biodiversity Information Facility',
                    'Library of Congress Control Number']

    while True:
        yield random.choice(merger_pages)


def generate_splitters():
    splitter_pages = ['Popular music pedagogy', 'PRDM2', 'Pressure reactivity index', 'Princess seams',
                      'Prison Memoirs of an Anarchist', 'Professional Football Sports Association',
                      'Programming Language for Business', 'PROP1', 'Proton-sensing G protein-coupled receptors',
                      'Ptarmigan Pass (Front Range)', 'R. G. de S. Wettimuny', 'Raco Army Airfield',
                      'RAF Bomber Command aircrew of World War II', 'Rajalakshmi School of Architecture',
                      'Rancho San Francisquito (Dalton)', 'Raoul Lefֳ¨vre', 'Ratneshwar Mahadev temple',
                      'Recipients of the Legion of Merit', 'Record-Rama',
                      'Results of the Japanese general election, 2009', 'Ricki & Copper', 'Roald Glacier', 'RU-28306',
                      'Russian Armed Forces casualties in Syria', 'Ryֵji Chֵ«bachi', 'Sֵiku Shigematsu',
                      'Safire Theatre complex', 'Saint Michael\'s Roman Catholic Church & Rectory',
                      'Saint Nicholas Greek Orthodox Cathedral (Pittsburgh)', 'Samsung Galaxy C7',
                      'San Felipe de Austin State Historic Site', 'San Juan Hill order of battle',
                      'San Luis National Wildlife Refuge Complex', 'Sapt Kranti Express', 'Sarvanivarana-Vishkambhin',
                      'Saulxures, Haute-Marne', 'Sayadaw U Tejaniya', 'Schiller Elementary School',
                      'Scottish Games in North Carolina', 'Secrets of Sarlona', 'Self-disorder',
                      'Sellers House (Pittsburgh, Pennsylvania)', 'Senate Constitutional Amendment No. 5',
                      'Sex hormone receptor', 'Shahira Amin', 'Shantadurga Kalangutkarin Temple', 'Sheja Dzֳ¶',
                      'Shields of the Revolution Council', 'Shooting at the 2008 Summer Olympics ג€“ Qualification',
                      'Shoup\'s Mountain Battery', 'Shravana (hearing)', 'Sinking Creek Raid',
                      'Sisters of the Company of Mary, Our Lady', 'Sitaramdas Omkarnath',
                      'Solar eclipse of August 28, 1848', 'Solar eclipse of May 7, 1902',
                      'Solar eclipse of October 31, 1902', 'South Dakota Legislative Research Council',
                      'South Side High School (Pittsburgh, Pennsylvania)', 'South Side Market Building',
                      'St. Clair Incline', 'St. Clair Village', 'St. Philomena\'s Church (Pittsburgh)',
                      'Stadium Authority of the City of Pittsburgh', 'Stan Wawrinka career statistics',
                      'Stanwix Street (Pittsburgh)', 'Steel Valley (Pittsburgh)', 'Stevens Elementary School',
                      'Straumnes Air Station', 'Structure of the French Army in 1989',
                      'Structure of the Hellenic Air Force', 'Subong', 'Super Singer Junior (season 2)',
                      'Suqour al-Ezz', 'Syrian National Resistance', 'Table of stars with Bayer designations',
                      'Tashi Tsering (Chenrezig Institute)',
                      'Technological and industrial history of 20th-century Canada', 'Televisiֳ³ Digital Terrestre',
                      'Testosterone acetate', 'Testosterone valerate', 'Thalamiflorae', 'The Atruaghin Clans',
                      'The Boatman\'s Dance', 'The Gathering 2009', 'The Jew in the Lotus',
                      'The Lives of Dutch painters and paintresses', 'The Mabuhay Channel', 'The Masked Marauders',
                      'The Old Path', 'The Projection Booth', 'Third Bardor Tulku Rinpoche', 'Thiru Vi. Ka. Bridge',
                      'Thubten Gyatso (Australian monk)', 'Timeline of Caen', 'Timeline of Cambridge, Massachusetts',
                      'Timeline of Chennai history', 'Timeline of Clermont-Ferrand', 'Timeline of Copenhagen',
                      'Timeline of Gold Coast, Queensland', 'Timeline of Grenoble', 'Timeline of healthcare in China',
                      'Timeline of Homs', 'Timeline of Kaliningrad', 'Timeline of Madrid', 'Timeline of Mulhouse',
                      'Timeline of Nantes', 'Timeline of Newark, New Jersey', 'Timeline of Nice',
                      'Timeline of Portuguese history (Lusitania and Gallaecia)', 'Timeline of Reims',
                      'Timeline of Rouen', 'Timeline of the 21st century',
                      'Timeline of the feminist art movement in New Zealand', 'Timeline of Toulon',
                      'Timeline of women in religion', 'Tool use by sea otters', 'Troy Hill Incline', 'Trudeau Landing',
                      'Tsukuba FC', 'Udumbara (Buddhism)', 'UFC All Access', 'Ugraparipב¹›cchִ Sֵ«tra',
                      'University of Pennsylvania College of Arts & Sciences',
                      'University of Texas at Austin admissions controversy',
                      'Uttar Pradesh Expressways Industrial Development Authority', 'Varennes-sur-Amance',
                      'Vasilisa Kozhina', 'VER-3323', 'Vic Cianca', 'Victoria Hall (Pittsburgh)',
                      'Virginia\'s 5th congressional district election, 2010',
                      'Virginia\'s 8th congressional district election, 2010', 'Virtual Museum of Protestantism',
                      'Vishva', 'Volazocine', 'Von Sternberg House', 'VP-44 (1951-91)', 'Walery Mroczkowski',
                      'Walker-Ewing Log House', 'Walkman X Series', 'Wall Tax Road, Chennai', 'Walter Nowick',
                      'Wansong Xingxiu', 'Warembori language', 'Waterfalls of North Georgia', 'Werner Leinfellner',
                      'West End Branch of the Carnegie Library of Pittsburgh', 'Westinghouse Atom Smasher',
                      'Westinghouse Memorial', 'William H. Davis (sheriff)', 'William Nyogen Yeo',
                      'William Penn Snyder House', 'Willmar Air Force Station', 'Wilson Glacier',
                      'WLQR (defunct 1450 AM)', 'Women\'s liberation movement in Europe', 'Women in Latin music',
                      'Women in Philippine art', 'Women in the Philippine National Police', 'Wotuג€“Wolio languages',
                      'Wukong (monk)', 'Wytheville Raid', 'Yogadב¹›ב¹£ב¹­isamuccaya', 'Zenitism']

    while True:
        yield random.choice(splitter_pages)


def generate_rares():
    rare_pages = ['Athene (disambiguation)', 'Alexandrists', 'The Triumph of Time', 'Billion (disambiguation)',
                  'Civil law', 'Chronometer', 'Clabbers', 'Diaeresis', 'Eiffel', 'First-order predicate',
                  'Four Pillars', 'Gilbert Cesbron', 'Groningen (disambiguation)', 'Goodtimes virus',
                  'George Robert Aberigh-Mackay', 'Image and Scanner Interface Specification', 'Jan Berglin',
                  'Jabal Ram', 'Jehoram', 'Joliet', 'Kocherג€“Debreג€“Semelaigne syndrome', 'Large technical system',
                  'Martin Luther King (disambiguation)', 'Value (poker)', 'Perfect crystal', 'Partizan Press',
                  'Phoniatrics', 'Persistence', 'PackBits', 'Slavic', 'Second-order predicate', 'Sleet',
                  'Samuel Huntington', 'Lisa Beamer', 'USS Memphis', 'USS Reuben James', 'Bob Welch', 'Thebes',
                  'Tuning', 'Dual mode propulsion rocket', 'USS Mustin', 'Adaptive communications',
                  'Amplitude distortion', 'Antenna blind cone', 'Bandwidth compression', 'Data access arrangement',
                  'Double-sideband reduced-carrier transmission', 'Managed object', 'Password length parameter',
                  'Power-law index profile', 'Stop signal', 'System integrity', 'Technical control facility',
                  'Zip-cord', 'USS Skate', 'Developing (film)', 'Mughal', 'Ganja', 'Straw man proposal', 'Ustad Isa',
                  'Jassy', 'DARPA TIDES program', 'Schema', 'National Liberation Army', 'Clarke County',
                  'Kent M. Keith', 'Hamilton County', 'Goddess worship', 'Number of the Beast (disambiguation)',
                  'Aeroport', 'Cubomania', 'Peter Murphy', 'Upcard', 'Clinton County', 'Petropavlovsk',
                  'Teleportation (disambiguation)', 'Fis phenomenon', 'Suomi', 'Wolfsbane', 'ARITH-MATIC', 'MC ADE',
                  'Maggotron', 'Illyricum', 'Mrs. Miniver\'s problem', 'USS Constellation', 'Dunedin (disambiguation)',
                  'Fort Nassau', 'Pashto (disambiguation)', 'Perennial (disambiguation)', 'James W. Prescott',
                  'Abel-mizraim', 'Amaziah', 'Anab', 'South American economic crisis of 2002', 'Shecaniah', 'IBM 3720',
                  'Post-surrealism', 'Cologne: From the Diary of Ray and Esther', 'Multiple Sidosis', 'The Nutshell',
                  'Trance and Dance in Bali', 'Palestinian Society for the Protection of Human Rights', 'Salamis',
                  'Podarge', 'Sequenced Packet Exchange', 'Pan (crater)', 'Xanthius', 'Phaedriades', 'Kickstart',
                  'Xingu', 'Shelby County', 'Jacob\'s Mouse', 'Theias', 'Pacemaker (disambiguation)', 'Lace card',
                  'Hesperis (mythology)', 'Ardeas', 'Hylaeus and Rhoecus', 'Tegyrios', 'Lyncus', 'Fulgora (mythology)',
                  'Mens', 'Suadela', 'Verminus', 'Artume', 'TNG', 'Hannover-Nordstadt', 'Vichama',
                  'Australian (disambiguation)', 'Bagadjimbiri', 'Birrahgnooloo', 'Gnowee', 'Kidili', 'Wuriupranili',
                  'ִ€rohirohi', 'Atanua', 'Auahitֵ«roa', 'Ratumaibulu', 'Murimuria', 'Irawaru', 'Lona (mythology)',
                  'Shakpana', 'Wroxham Broad', 'Pacific Maritime Association', 'Norֳ°urmֳ½ri',
                  'Bure Marshes National Nature Reserve', 'National nature reserves in Bedfordshire',
                  'Quartet in Autumn', 'Harken Energy scandal', 'George McClellan (disambiguation)',
                  'Zablujena generacija', 'Crystal Lake (Broward County, Florida)', 'Sluis-Aardenburg',
                  'New Kuomintang Alliance', 'Colfax Township, Michigan', 'Clinton, New York',
                  'Brady Township, Pennsylvania', 'Carroll Township, Pennsylvania', 'Centre Township, Pennsylvania',
                  'Clinton Township, Pennsylvania', 'Delaware Township, Pennsylvania', 'Earl Township',
                  'Green Township, Pennsylvania', 'Hamilton Township, Pennsylvania', 'Limestone Township, Pennsylvania',
                  'Londonderry Township, Pennsylvania', 'Manheim Township, Pennsylvania',
                  'Morris Township, Pennsylvania', 'Newtown Township, Pennsylvania', 'Richland Township, Pennsylvania',
                  'Rush Township, Pennsylvania', 'Salem Township, Pennsylvania', 'Scott Township, Pennsylvania',
                  'Shenango Township, Pennsylvania', 'Smithfield Township, Pennsylvania',
                  'Spring Township, Pennsylvania', 'Summit Township, Pennsylvania', 'Barth', 'Jan Bake', 'Mark Retera',
                  'Bure Valley Path', 'Grֳ¦sted-Gilleleje', 'David Stephenson (born 1972)', 'Birmingham Dribbler',
                  'Aaskov Municipality', 'Superposition', 'Situational offender', 'River Stour', 'Bountiful Harvest',
                  'Yorktown', 'Britten (disambiguation)', 'Hippocratic face', 'Brooke', 'Knֳ₪ck',
                  'Francisco Castro (Portuguese footballer)', 'Robert B. Hawkins Jr.', 'Defect', 'Pareto interpolation',
                  'Gandalf (theorem prover)', 'Topeka (store)', 'From Stump to Ship', 'River Tame', 'Albanian', 'Httpd',
                  'Electronic imager', 'Cheap Truth', 'Guinea Grass', 'Trial Farm', 'Saddam (name)', 'Aisha Kahlil',
                  'HiDef', 'Vise (disambiguation)', 'USS Nebraska', 'Jeanne Julia Bartet', 'Surautomatism', 'Bֳ¸',
                  'Jupiter Cantab', 'Silent Snow, Secret Snow', 'Stadium (disambiguation)', 'Nernst heat theorem',
                  'Dominican', 'On Watanabe', 'Tsunashima Ryֵsen', 'Teikoku Bungaku', 'Structural road design',
                  'Ishibashi Ningetsu', 'Enzo Matsunaga', 'USS Brooklyn', 'USS Langley', 'Stammer (disambiguation)',
                  'All-silica fiber', 'Major consensus narrative', 'USS New Hampshire', 'The Bad Examples',
                  'USS New Jersey', 'LCFG', 'Uff!', 'Thomas Fairfax (disambiguation)', 'Stamitz', 'John Sanford',
                  'Derek V. Smith', 'Tiki Data', 'Fluorescent multilayer card', 'Gordon S. Fahrni', 'Shuntֵ', 'AVIDAC',
                  'Istanbul cymbals', 'Treatment', 'South East Point', 'Babel (newspaper)', 'USS Tarawa', 'Calisia',
                  'Stonehouse Creek', 'William B. Ellern', 'USS Badger', 'Laban Ainsworth', 'John Morton-Finney',
                  'The Nigger', 'Everybody\'s Autobiography', 'Twilight Club', 'USS Astoria', 'Bobby Pacho',
                  'Lunar conjunction', 'Andrew George Burry', 'Prime reciprocal magic square',
                  'Uncle and His Detective', 'USS Tiger Shark', 'Faculty', 'Oִuz Yִ±lmaz',
                  'Santa Monica (disambiguation)', 'Hellerud', 'Names (disambiguation)',
                  'Hsiangג€“Lawson\'s conjecture', 'Victory Song (horse)', 'Security for costs',
                  'Soviet submarine K-129', 'Paul Petard', 'Generalised logistic function', 'Wort (disambiguation)',
                  'Floradora', 'Set and drift', 'Meaningless statement', 'Indigenous', 'The Naked Eye (1956 film)',
                  'Charles Ollivant', 'Gaston Briart', 'Blanketing', 'Larry Burns (General Motors)', 'Acrylic',
                  'Holy Wood', 'Shadow government', 'Container (disambiguation)', 'Free enterprise (disambiguation)',
                  'Buy', 'Cryoelectronics', 'Anna Santisteban', 'Affect', 'Elisabeth of Austria', 'Advice',
                  'TenDRA Distribution Format', 'Public Schools Act', 'Thurston elliptization conjecture',
                  'Numerical sight-singing', 'Aquila Romanus', 'Brute force', 'Capital Adequacy Directive',
                  'Medallion Records', 'Caron (disambiguation)', 'Evil Empire', 'Tia (goddess)', 'Mona Font', 'Sensory',
                  'More Joy in Heaven', 'San Antonio, Cayo', 'Morgan County', 'GE multifactoral analysis',
                  'Masculine (disambiguation)', 'Feminine (disambiguation)', 'Gabriel Parra', 'Bormann',
                  'Fifth Republic', 'Women Thrive Worldwide', 'Bath brick', 'Pre-flashing', 'Restricted product',
                  'George Amabile', 'Paullus', 'Macrovascular disease', 'Malvinas (disambiguation)', 'Chinese tabloid',
                  'Sound system', 'Piru (spirit)', 'Robert Budde', 'New Zealand Prostitutes\' Collective', 'Eof',
                  'Richard Jobson (explorer)', 'Stress test', 'Il Risorgimento (newspaper)',
                  'Sir William Blackstone (statue)', 'Threat of force (public international law)',
                  'Saint Mary\'s River', 'Plachutta', 'Kjelfossen', 'Tyssestrengene', 'Blackwardine', 'Alan Haig-Brown',
                  'USS Cumberland', 'USS Denver', 'Battle of Quebec', 'Socialist Unity Party', 'A Gift Upon the Shore',
                  'Peijaiset', 'Gillingham', 'HMS Upholder', 'Mixed franking', 'Bruun\'s FFT algorithm',
                  'In-band adjacent-channel', 'Intersection syndrome', 'Saint-Jean County, Quebec', 'Ardagh',
                  'Uppland County', 'Timetable (disambiguation)', '4VSB', '2VSB', 'Daniel Kriegman',
                  'Situationist Antinational', 'Tim Lander', 'Gwenllian', 'Drift migration', 'What More Can I Ask?',
                  'Email art', 'Nicole Markotic', 'Shirlee Matheson', 'Symbolics Document Examiner', 'La Rochefoucauld',
                  'Charles Gray', 'Gurcharan Rampuri', 'National Health Planning and Resources Development Act',
                  'El Ausente', 'Commute', 'Richard Stevenson (poet)', 'Dan Miller', 'Norwegian Student Choral Society',
                  'All Species Foundation', 'South Branch', 'Pariah Press', 'Hotter\'N Hell Hundred',
                  'Obfuscated Perl Contest', 'Negrita Jayde', 'Chinese nationality', 'Consejo',
                  'Thomas Tanner (writer)', 'Watermedia', 'Evar Saar', 'Alomancy', 'Benton County', 'Tursib', 'Gorki',
                  'Shiroka Polyana', 'Midwest Christian Outreach', 'Adamantine Spar',
                  'Lossless Transform Audio Compression', 'Background (astronomy)', 'Richard Wawro', 'Irma Brandeis',
                  'Bentonville', 'Bruckner (disambiguation)', 'Tiberius Sempronius Gracchus', 'Appel', 'Smale',
                  'Laura Recovery Center', 'Shaded-pole synchronous motor', 'Frank Houben', 'USS Anzio',
                  'Merchandization', 'Meiklejohn Civil Liberties Institute', 'Eduard Haas', 'Sacred band',
                  'Eddie Lֳ³pez (boxer)', 'Good Neighbour Policy (horse racing)', 'Logical topology',
                  'Biltmore Records', 'Kinthup', 'Cֳ₪sar Rֳ¼stow', 'Dial Records', 'Gyeongbu', 'Subtle cardinal',
                  'TimeShard', 'Gimpo Line', 'Lakeside Records', 'Freshwater shark', 'Sitwell', 'Geir Barvik',
                  'Universal dialectic', 'Aivaras', 'Pulper', 'Larousse', 'Treatise (music)', 'Fourth Republic',
                  'Broadcast Twelve Records', 'Schirmer Records', 'Hacִ±osman, Manyas', 'The Rockies (disambiguation)',
                  'Bel-Air (Sanford)', 'Gyro', 'Carlea, Saskatchewan', 'Mean deviation', 'William Hearst',
                  'Makoto Tomioka', 'Priszm', 'Ear tuft', 'Foreign Correspondents\' Club, Phnom Penh', 'Ryosuke Cohen',
                  'Ernest Maas', 'Laplace transform applied to differential equations',
                  'Resource Directory Description Language', 'Rinken Band', 'Tommy Solomon', 'Oriental Sports Daily',
                  'Oscar Kjellberg', 'Akizuki Tanezane', 'Herbede', 'Nagoya, Saga', 'Chris Carter', 'Norrland County',
                  'Gֳ¶ta', 'Unicoherent space', 'William Robert Renshaw', 'Colombeau algebra',
                  'Change the World Without Taking Power', 'Rank (computer programming)', 'Perle',
                  'Bank of America Plaza', 'Brahma (disambiguation)', 'Bobbin boy', 'The Secret of the Universe',
                  'Rojam', 'Portable communications device', 'Artaxerxes', 'Anyonic Lie algebra', 'Somali',
                  'Multimagic square', 'Wire loop game', 'Antifa', 'Crumb', 'Tropic (disambiguation)',
                  'Hermia (Finland)', 'Bai Hua', 'Midian war', 'Baluchi', 'Kedermister Library',
                  'Decalogue (disambiguation)', 'Sergei Ivanovich Tiulpanov', 'The Mississauga Horse',
                  'Hicks (disambiguation)', 'Nauru Pacific Line', 'Ordinance (university)', 'Water lily',
                  'Captain Submarine', 'Przemyֵ›l (disambiguation)', 'Robert Kite', 'Meramec', 'Richard Grosvenor',
                  'Commie Awards', 'Kalinovka, Khomutovsky District, Kursk Oblast', 'Office of Special Investigations',
                  'Scarcity value', 'Free floating screed', 'Sons of Poland', 'Chairman of the Board (disambiguation)',
                  'Weak consistency', 'Maven (Scrabble)', 'Muncie', 'Shower-curtain effect', 'Product description',
                  'Abbey of St. Jean des Vignes', 'Cummings', 'Riksdagsmusiken', 'Engel', 'Santorum (disambiguation)',
                  'Luitgard (Frankish queen)', 'International Pentecostal Church of Christ',
                  'Fixed-point lemma for normal functions', 'USS Bonefish', 'USS Holland', 'Peltier', 'Tollbooth',
                  'Jack Cohen', 'Elmwood Park', 'Daarlerveen', 'Republican People\'s Party', 'United Party',
                  'USS Alexander Hamilton', 'Succession planting', 'Jiefang Subdistrict, Zhoushan', 'Edward Hartman',
                  'Desmond Keith Carter', 'Lynnville', 'Bible box', 'Gether', 'Operation Adler',
                  'British-American Parliamentary Group', 'Bisbee Blue', 'Piano Sonatas Nos. 13 and 14 (Beethoven)',
                  'Aweida', 'Agency for Nuclear Projects', 'Caguax', 'Friedrich August Berthold Nitzsch', 'Upper Weald',
                  'Robert Atkins', 'HMS Manchester', 'Ronald Campbell', 'Carlton House desk', 'Histochemical tracer',
                  'The Breetles', 'Papandreou', 'Grammy Award for Best New Country & Western Artist',
                  'Socialism from below', 'Content package', 'Ostrֳ³w Island', 'Islands of Gdaֵ„sk',
                  'Quarantine (Egan novel)', 'USS Coral Sea', 'USS Cowpens', 'USS Iwo Jima', 'USS Valley Forge',
                  'USS Wright', 'Technique', 'Jenny Jones', 'Heronian tetrahedron', 'Ezboard', 'Otterton Mill',
                  'HMS Flamingo', 'HMAS Stalwart', 'HMAS Swan', 'Literary Machines', 'Cayleyג€“Galt Tariff', 'Rooney',
                  'Richard Carpenter', 'AS/400 object', 'HMS Oberon', 'USS Charlotte', 'USS Chattanooga',
                  'Nomen mysticum', '2 mm scale', 'USS Albemarle', 'USS Archerfish', 'USS Catawba', 'Moqua Well',
                  '51st Division', 'California 4th Grade Mission Project', 'Henri Maillardet', 'Dara Nur al-Din',
                  'Kamel al-Kilani', 'Masaryk', 'Karzai (surname)', 'Michael Morris', 'Expert determination',
                  'Irana Esperantisto', 'Tullio Moneta']

    while True:
        yield random.choice(rare_pages)


def pull_game(gameType, imp_gen, split_gen, marge_gen, rare_gen):
    if gameType == "random":
        return wikipedia.random(), wikipedia.random()
    if gameType == 'impulsive':
        return next(imp_gen)
    if gameType == 'natural':
        return next(split_gen), next(marge_gen)
    if gameType == 'extreme':
        return next(marge_gen), next(split_gen)
    if gameType == 'niche':
        return next(rare_gen), next(rare_gen)

    raise Exception(gameType + " is not well define")


def parse_run(start_art, end_art, algo, forward, backward):
    fpath, bpath, fopen, bopen, total_time, depth = run(start_art, end_art, algo, forward, backward)
    path = " -> ".join(fpath) + " | " + " -> ".join(bpath)
    total_time = round(total_time / 60, 2)
    print("  ", depth, path)
    print("  opened from start:", fopen, "opened from end:", bopen)
    print("  took: ", total_time, "mins")
    return path, bopen, fopen, total_time, depth


def short_test_heuristic(algo, forward, backward=None):
    print('--------now testing heuristic', algo.__name__, 'with', forward.__name__, "and", backward.__name__,
          'shortly -------------------')
    print('genre: impulsive choice')
    generator = generate_popular_pages()
    for i in range(5):
        start_art, end_art = next(generator)
        print('  run from %s to %s...' % (start_art, end_art))
        parse_run(start_art, end_art, algo, forward, backward)

    print('genre: hierarchy tasks')

    start_art, end_art = "Quark", "Marble"
    print('  run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Marble", "Quark"
    print('  and backwards: run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Slender-snouted_crocodile", "Flatworm"
    print('  run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Flatworm", "Slender-snouted_crocodile"
    print('  and backwards: run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Ossicles", "Glomerulus_(kidney)"
    print('  path between edges : run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    print('genre: extreme tasks')
    start_art, end_art = "Ossicles", "Glomerulus_(kidney)"
    print('  path between edges : run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))


def extreme_test_heuristic(rounds, gameTypes, methods):
    print('--------now testing heuristic overnight for %s rounds, %s gameTypes and %s methods -------------------' % (
        str(rounds), str(len(gameTypes)), str(len(methods))))

    impulsive = generate_popular_pages()
    mergers = generate_mergers()
    splitters = generate_splitters()
    rare = generate_rares()

    file = open("extreme_test_results" + time.ctime().replace(' ', '_').replace(':', '_') + ".txt", 'w', 1)

    file.write(
        'genre\talg-fHeu-bHeu\tstart_art\tend-art\tdepth\topened-src\topend-dest\topened-total\ttime\tpath\terrors\n')

    for rouns in range(rounds):
        for gameType in gameTypes:
            start_art, end_art = pull_game(gameType, impulsive, mergers, splitters, rare)

            for method in methods:

                algo, forward, backward = method
                methodName = algo.__name__ + '-' + forward.__name__ + "-" + backward.__name__
                printble_start_art = "".join(list(filter(lambda x: x in printable, start_art)))
                printble_end_art = "".join(list(filter(lambda x: x in printable, end_art)))
                file.write('\t'.join([gameType + ' choice', methodName, printble_start_art, printble_end_art]))

                try:
                    print("runing %s from %s to %s" % (methodName, start_art, end_art))
                    pool = mp.Pool(processes=1)
                    single_test_thread = pool.apply_async(parse_run, args=[start_art, end_art, algo, forward, backward])
                    try:
                        path, bopen, fopen, run_time, depth = single_test_thread.get(timeout=TIMEOUT)
                        file.write('\t'.join(
                            ["", str(depth), str(fopen), str(bopen), str(bopen + fopen), str(run_time), path, '\n']))
                        pool.close()

                    except mp.TimeoutError:
                        pool.terminate()
                        pool.close()
                        raise Exception('failed to work withing %s minuets' % str(TIMEOUT/60))
                except Exception as e:
                    file.write('\t-\t-\t-\t-\t-\t-\t' + str(e) + '\n')

    file.close()


def run_tests():
    methods = []
    methods += [(bidirectional_a_star, bfs_heuristic, bfs_heuristic)]  # bfs
    methods += [(bidirectional_a_star, random_heuristic, random_heuristic)]  # random
    methods += [(a_star_search, random_heuristic, random_heuristic)]  # random
    methods += [(bidirectional_a_star, bow_heuristic, bow_heuristic)]  # bow
    methods += [(bidirectional_a_star, language_heuristic, language_heuristic)]  # lang
    methods += [(bidirectional_a_star, metadata_heuristic, metadata_heuristic)]  # categories
    methods += [(bidirectional_a_star, splitter_rank_heuristic, merger_rank_heuristic)]  # better-than-dad
    methods += [(bidirectional_a_star, FeaturesHeuristic().features_heuristic,
                 FeaturesHeuristic().features_heuristic)]  # features-heuristic
    game_types = []
    game_types += ["impulsive"]
    game_types += ["random"]
    game_types += ["natural"]
    game_types += ["niche"]
    game_types += ["extreme"]
    extreme_test_heuristic(1000, game_types, methods)
    print('DONE')


def main():
    heuristics = ["bfs_heuristic", "bow_heuristic", "metadata_heuristic", "splitter_rank_heuristic",
                  "merger_rank_heuristic", "language_heuristic", "features_heuristic",
                  "random_heuristic"]
    usage = """
    Usage: executor.py [options]

    Options:
    -s, --start                 start article
    -e, --end                   goal article
    -f, --forward_heuristic     heuristic to use in forward search
    -b, --backward_heuristic    heuristic to use in backward search
    -t --tests                  run tests only
    """
    parser = OptionParser(usage)

    parser.add_option('-s', '--start', dest='start',
                      default=None,
                      help='start article')

    parser.add_option('-e', '--end', dest='end', default=None,
                      help='end article')

    parser.add_option('-f', '--forward_heuristic', dest='forward_heuristic',
                      help='forward heuristic',
                      choices=heuristics,
                      default='splitter_rank_heuristic')

    parser.add_option('-b', '--backward_heuristic', dest='backward_heuristic',
                      help='backward heuristic', default='merger_rank_heuristic',
                      choices=heuristics)
    parser.add_option("-t", "--tests", action="store_true", dest="tests")
    options, args = parser.parse_args()

    if options.tests:
        return run_tests()
    if options.start is None or options.end is None:
        print("You must specify a start article and a goal article!")
        parser.print_usage()
        return
    try:
        fh = getattr(sys.modules[__name__], options.forward_heuristic)
    except AttributeError:
        fh = FeaturesHeuristic().features_heuristic
    try:
        bh = getattr(sys.modules[__name__], options.backward_heuristic)
    except AttributeError:
        bh = FeaturesHeuristic().features_heuristic
    fpath, bpath, fopen, bopen, total_time, len_path = run(start=options.start, end=options.end,
                                                                   algo=bidirectional_a_star,
                                                                   forward_heu=fh, backward_heu=bh)
    total_path = fpath + bpath[1:]
    print(" --> ".join([x.replace("_", " ") for x in total_path]))

if __name__ == "__main__":
    main()
