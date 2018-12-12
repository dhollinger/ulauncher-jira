# -*- coding: utf-8 -*-
""" Created by Safa Arıman on 12.12.2018 """
import base64
import json
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import urllib
import urlparse
import urllib2
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

__author__ = 'safaariman'


class ExtensionKeywordListener(EventListener):

    def __init__(self, icon_file):
        self.icon_file = icon_file

    def on_event(self, event, extension):
        query = event.get_argument()
        results = []

        workspace_url = extension.preferences.get('url')
        user = extension.preferences.get('username')
        password = extension.preferences.get('password')

        token = base64.b64encode(str('%s:%s' % (user, password)).encode()).decode()
        url = urlparse.urljoin(workspace_url, 'rest/internal/2/productsearch/search')
        get_url = "%s?%s" % (url, urllib.urlencode({'q': query}))
        req = urllib2.Request(get_url, headers={'Authorization': 'Basic %s' % token})

        result_types = []

        try:
            response = urllib2.urlopen(req)
            result_types = json.loads(response.read())
        except urllib2.HTTPError as e:
            if e.code == 401:
                results.append(
                    ExtensionResultItem(
                        name='Authentication failed.',
                        description='Please check your username/e-mail and password.',
                        icon=self.icon_file,
                        on_enter=DoNothingAction()
                    )
                )
            return RenderResultListAction(results)
        except urllib2.URLError as e:
            results.append(
                ExtensionResultItem(
                    name='Could not connect to Jira.',
                    description='Please check your workspace url and make sure you are connected to the internet.',
                    icon=self.icon_file,
                    on_enter=DoNothingAction()
                )
            )
            return RenderResultListAction(results)

        print(json.dumps(result_types))

        for rtype in result_types:
            for item in rtype.get('items', []):
                key = item.get('subtitle')
                title = item.get('title')
                url = item.get('url')
                results.append(
                    ExtensionResultItem(
                        name=title if not key else '%s - %s' % (key, title),
                        description=key,
                        icon=self.icon_file, on_enter=OpenUrlAction(url=url))
                )

        if not results:
            results.append(
                ExtensionResultItem(
                    name="Search '%s'" % query,
                    description='No results. Try searching something else :)',
                    icon=self.icon_file,
                    on_enter=DoNothingAction())
            )

        return RenderResultListAction(results)
