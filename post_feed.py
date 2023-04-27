import feedparser
import markdownify
import webpreview
from monstr.ident.alias import ProfileFileAlias
from monstr.ident.profile import Profile
from monstr.encrypt import Keys


class RSSPoster:

    def __init__(self, alias_file: str):
        self._alias = ProfileFileAlias(alias_file)

    def get_profile(self, profile_name: str) -> Profile:
        return self._alias.get_profile(profile_name)

    def add_profile(self, p: Profile):
        self._alias.put_profile(p)
        self._alias.save()

    def _attrs_from_rss(self, rss_url: str, attrs: dict):
        if 'title' not in attrs or \
                'desc' not in attrs or \
                'img' not in attrs:
            feed_data = feedparser.parse(rss_url)
            if 'title' in feed_data.feed and attrs['title'] is None:
                attrs['title'] = feed_data.feed.title
            if 'subtitle' in feed_data.feed and attrs['desc'] is None:
                attrs['desc'] = feed_data.feed.subtitle
            if 'logo' in feed_data.feed and attrs['image'] is None:
                attrs['image'] = feed_data.feed.logo

    @staticmethod
    def _attrs_from_site(site_url: str, attrs: dict):
        if 'title' not in attrs or\
                'desc' not in attrs or\
                'img' not in attrs:

            # fetch site tags
            preview = webpreview.webpreview(site_url)

            if preview.title and attrs['title'] is None:
                attrs['title'] = preview.title
            if preview.description and attrs['desc'] is None:
                attrs['desc'] = preview.description
            if preview.image and attrs['image'] is None:
                attrs['image'] = preview.image

    def new_profile(self,
                    profile_name: str,
                    rss_url: str,
                    site_url: str = None,
                    name: str = None,
                    title: str = None,
                    desc: str = None,
                    img: str = None) -> Profile:

        # if not given just name the account as the profile_name/alias
        if name is None:
            name = profile_name

        # now set the attrs, from caller
        attrs = {
            'name': name,
            'title': title,
            'desc': desc,
            'image': img,
            'rss_url': rss_url
        }

        if site_url:
            attrs['site_url'] = site_url

        # if site_url try from that
        if site_url:
            self._attrs_from_site(site_url, attrs)

        # if still unavailable check the rss_feed
        self._attrs_from_rss(rss_url, attrs)

        # add description
        about = ''
        if attrs['title']:
            about = '%s\n' % attrs['title']

        if attrs['desc']:
            about = about + attrs['desc'] +'\n'

        attrs['about'] = about + site_url

        del attrs['title']
        del attrs['desc']
        for k in attrs.keys():
            if attrs[k] is None:
                del attrs[k]



        # create profile with new key
        p = Profile(priv_k=Keys().private_key_hex(),
                    profile_name=profile_name,
                    attrs=attrs)
        # FIXME: this should break if we attempt to put a profile that already exists but mem store isnt checking this
        self.add_profile(p)


my_poster = RSSPoster('~/.nostrpy/rss_mappings.csv')
bbc_news_rss = my_poster.get_profile('bbc_news_rss')
if bbc_news_rss is None:
    my_poster.new_profile(profile_name='bbc_news_rss',
                          site_url='https://www.bbc.co.uk/news',
                          rss_url='https://feeds.bbci.co.uk/news/rss.xml?edition=uk')

the_register_rss = my_poster.get_profile('theregister_rss')
if the_register_rss is None:
    my_poster.new_profile(profile_name='theregister_rss',
                          site_url='https://www.theregister.com',
                          rss_url='https://www.theregister.com/headlines.atom')

print(bbc_news_rss.get_attr('rss_url'))


# feed_url = 'https://feeds.bbci.co.uk/news/rss.xml?edition=uk'
# feed_url = 'https://www.theregister.com/headlines.atom'
#
# d = feedparser.parse(feed_url)
# for c_art in d.entries:
#     print(c_art.title)
#     print(markdownify.markdownify(c_art.summary))