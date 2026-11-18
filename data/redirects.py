# Addresses of the old WordPress site (captured by the Wayback Machine, 2021 to 2024) and where they now point.
# build.py writes a small redirect page at each old address, unless a real page now lives there
# (e.g. if one of the two 2021 blog posts is published again at its original URL).
OLD_SITE = {
    "/book/": "/publications/",
    "/research/": "/expertise/",
    "/giving/": "/about/",
    "/in-the-media/": "/media/",
    "/photography/": "/about/",
    "/blog/": "/",
    "/contact/": "/#contact",
    "/author/ogandhi/": "/about/",
    "/category/academic/": "/publications/",
    "/category/getting-published/": "/publications/",
    "/getting-your-paper-camera-ready/": "/",
    "/increasing-your-research-output-and-others-by-becoming-a-co-author/": "/",
}
