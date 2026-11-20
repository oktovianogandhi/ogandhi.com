# Media coverage, recognition, and talks for ogandhi.com, newest first.
# Fields: date (YYYY-MM or YYYY-MM-DD), outlet, title, url (leave "" if no working link), note (one sentence, optional),
# schema (schema.org type for structured data; default NewsArticle).
# Only link pages that load (checked 18 and 20 November 2026); use a Wayback Machine copy when the original is gone.
# The media page lists NEWS and RECOGNITION together, newest first (Okto, 20 November 2026); the home page shows the latest NEWS.
# Only repeat figures that are published (not SERIS database figures quoted in an article).
# Sources: the archived "In the Media" page of the old WordPress site (2021 to 2024) and a web search, November 2026.

NEWS = [
    dict(date="2026-11-17", outlet="AP News", title="Florida’s stormwater ponds become floating solar farms as costs fall and demand rises",
         url="https://apnews.com/article/sustainable-energy-floating-solar-florida-ef1138ee8804f96094ab521f7e1d0224",
         note="Quoted on how floating PV has matured and what it costs compared with land-based solar. Also carried by US News & World Report, Yahoo News, and WLRN."),
    dict(date="2021-10-25", outlet="Listrik Indonesia", title="Menerangi Remote Area Lewat Surya",
         url="https://listrikindonesia.com/detail/8530/menerangi-remote-area-lewat-surya",
         note="Interview on solar electrification of remote areas in Indonesia (in Indonesian)."),
    dict(date="2020-06-03", outlet="ScienceDaily", title="Double-sided solar panels that follow the sun prove most cost effective",
         url="https://www.sciencedaily.com/releases/2020/06/200603132543.htm",
         note="On our global study of bifacial modules and trackers, which was also covered by pv magazine, New Scientist, and Forbes."),
    dict(date="2019-05", outlet="Indonesia Mengglobal", title="Oktoviano Gandhi: Investing in Indonesia’s Solar Energy",
         url="https://indonesiamengglobal.com/2019/05/oktoviano-gandhi-solar-energy/", note="Interview."),
    dict(date="2019", outlet="St. Gallen Symposium", title="Interview with a Leader of Tomorrow 2019: Oktoviano Gandhi, Cofounder of Alva Energi",
         url="https://symposium.org/interview-with-a-leader-of-tomorrow-2019-oktoviano-gandhi-cofounder-of-alva-energi/",
         note="Selected as a Leader of Tomorrow for the 2019 St. Gallen Symposium."),
    dict(date="2013-03-25", outlet="Oxford Mail", title="Walks to be guided by those who know homelessness",
         url="https://www.oxfordmail.co.uk/news/10310569.walks-guided-know-homelessness/",
         note="On StreetView Oxford, the social enterprise I founded with Enactus Oxford."),
]

RECOGNITION = [
    dict(date="2021", outlet="Tatler Asia", title="Gen.T List 2021: Leaders of Tomorrow (Indonesia)",
         url="https://www.tatlerasia.com/people/oktoviano-gandhi", note="", schema="WebPage"),
    dict(date="2021-01", outlet="Solar Energy Research Institute of Singapore", title="Best Paper Award, IEEE WIECON-ECE 2020",
         url="https://www.seris.nus.edu.sg/achievements/best-paper-award-at-ieee-wiecon-ece-2020-dr-oktoviano-gandhi/",
         note="With co-authors, for a paper on dispatch planning for Singapore’s grid with PV and storage.", schema="WebPage"),
    dict(date="2020-07-13", outlet="NUS Electrical and Computer Engineering", title="Springer Thesis Award",
         url="https://cde.nus.edu.sg/ece/news/springer-thesis-award-dr-oktoviano-gandhi/",
         note="For my PhD thesis, published in the Springer Theses series.", schema="WebPage"),
    dict(date="2020-02", outlet="Vanity Fair and One Young World", title="A World of Good: the Global Goals List",
         url="http://web.archive.org/web/20230601160142/https://www.vanityfair.com/london/2020/02/one-young-world-summit-2019",
         note="Named for Sustainable Development Goal 7 (affordable and clean energy). Archived copy."),
    dict(date="2019", outlet="One Young World", title="30 young leaders building carbon-neutral futures to attend #OYW2019 via BP Scholarship",
         url="http://web.archive.org/web/20250619230006/https://www.oneyoungworld.com/news-item/30-young-leaders-building-carbon-neutral-futures-attend-oyw2019-bp-scholarship",
         note="BP Advancing Energy Scholar. Archived copy."),
    dict(date="2019", outlet="Global Young Scientists Summit, Singapore", title="Participant", url="", note="", schema="WebPage"),
]

# Selected talks and panels (Master Experience Register, section 7, and the old site's list).
TALKS = [
    dict(date="2026-09", outlet="Bali International Conference on Marine Floating Photovoltaics and Microgrids (Grantham Research Institute, LSE)",
         title="The economics of marine floating PV: cost structure, benchmarks, and pathways to parity", url="", note="Invited speaker."),
    dict(date="2024-10", outlet="2nd Korea–Singapore Joint Photovoltaic Symposium, Singapore", title="Invited speaker", url="", note=""),
    dict(date="2023-11", outlet="Photovoltaic & Storage ASEAN Conference & Expo, Jakarta",
         title="ASEAN photovoltaic market forecast and future prospects", url="",
         note="Invited speaker; also a panellist on floating solar PV with energy storage."),
    dict(date="2022-12", outlet="IEA PVPS Task 13 workshop on floating PV energy yield", title="Presented inputs from SERIS", url="", note=""),
    dict(date="2022-04", outlet="South Korea Renewable Energy Invest Indonesia 2022", title="Moderator, solar energy session", url="", note=""),
    dict(date="2020-12", outlet="ETH Zurich, Master of Advanced Studies in Development and Cooperation", title="Guest speaker", url="", note=""),
    dict(date="2020-06", outlet="Institute for Essential Services Reform (IESR), Jakarta",
         title="Meningkatkan Peran Energi Terbarukan dalam Mengatasi Tantangan Penyediaan Akses Energi",
         url="https://www.youtube.com/watch?v=ZKrkcvm87is",
         note="Panellist, with the Ministry of Energy and Mineral Resources, on renewable energy for energy access (in Indonesian; video)."),
    dict(date="2020-05", outlet="The ChangeMaker 2020", title="Solar-powered villages: utopian reality?", url="", note="Speaker (in Indonesian)."),
    dict(date="2019-03", outlet="Newcastle University, Singapore", title="Renewable energy technology", url="", note="Guest lecturer."),
    dict(date="2018-08", outlet="Arctic Renewable Energy Atlas (AREA) workshop, Energy Studies Institute, Singapore", title="Invited speaker", url="", note=""),
    dict(date="2018-07", outlet="ASEAN Centre for Energy, Jakarta", title="Techno-economic analysis of reactive power provision using PV", url="",
         note="Invited lecture; also presented to Bimasena, the Mines and Energy Society, in Jakarta."),
]
