import json
import requests
import argparse
import sys
from api_auth import APICredentials, APIParams, Signer


class LinearPlaylistAPI:
    def __init__(self):
        self.host = "http://services.uplynk.com"

    def create_linear_playlist(self, playlist_string, description, repeat, break_duration, skip_token, addslatefill,
                               active, drm_required):
        url = self._api_url()
        payload = self._get_create_update_linear_playlist_payload(playlist_string, description, repeat, break_duration,
                                                                  skip_token, addslatefill, active, drm_required)
        response = self._send_api_post_request(url, payload)
        if not self._is_api_error(response):
            json_response = response.json()
            print("Created playlist Response: ")
            print(json.dumps(json_response, indent=2))
            return json_response['id']

    def update_linear_playlist(self, plid, playlist_string, description, repeat, break_duration, skip_token,
                               addslatefill, active, drm_required):
        url = self._api_url() + plid
        payload = self._get_create_update_linear_playlist_payload(playlist_string, description, repeat, break_duration,
                                                                  skip_token, addslatefill, active, drm_required)
        response = self._send_api_patch_request(url, payload)
        if not self._is_api_error(response):
            json_response = response.json()
            print("Updated Playlist Response: ")
            print(json.dumps(json_response, indent=2))
            return json_response['id']

    def list_linear_playlist(self, plid=None):
        url = self._api_url(plid)
        response = self._send_api_get_request(url)
        if not self._is_api_error(response):
            print("Playlists: \n")
            print(json.dumps(response.json(), indent=2))

    def delete_linear_playlist(self, plid=None):
        url = self._api_url(plid)
        response = self._send_api_delete_request(url)
        if not self._is_api_error(response):
            print("Delete Success\n")

    def _api_url(self, plid=None):
        idstr = plid if plid else ''
        return "{}{}{}".format(self.host, "/api/v4/linear-playlist/", idstr)

    def _get_api_params(self):
        return APIParams(APICredentials()).get_params({})

    def _send_api_post_request(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            url, params=self._get_api_params(), data=json.dumps(payload), headers=headers
        )
        return response

    def _send_api_patch_request(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        response = requests.patch(
            url, params=self._get_api_params(), data=json.dumps(payload), headers=headers
        )
        return response

    def _send_api_get_request(self, url):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            url, params=self._get_api_params(), headers=headers
        )
        return response

    def _send_api_delete_request(self, url):
        headers = {'Content-Type': 'application/json'}
        response = requests.delete(
            url, params=self._get_api_params(), headers=headers
        )
        return response

    def _is_api_error(self, response):
        if response is None:
            # If we have no response lets assume success?
            print('No reponse - Assuming success')
            return False
        status_remnant = response.status_code - 200
        if 99 > status_remnant > 0:
            # 2xx error code, we have success
            return False
        json_response = response.json()
        print(json.dumps(json_response, indent=2))
        return True

    def _get_create_update_linear_playlist_payload(self, playlist_string, description, repeat, break_duration,
                                                   skip_token, addslatefill, active, drm_required):
        pl = []
        if playlist_string:
            pl_items = playlist_string.split(',')
            for item in pl_items:
                entry = {'beam': {'id': item}}
                if item.isnumeric():
                    entry = {'ad': {'dur': int(item)}}
                pl.append(entry)
            payload = {}

        payload = {}
        if addslatefill is not None:
            payload['ad_slate_fill'] = int(addslatefill)
        if active is not None:
            payload['active'] = int(active)
        if drm_required is not None:
            payload['studio_drm_required'] = int(drm_required)
        if skip_token is not None:
            payload['skip_drm'] = int(skip_token)
        if description is not None:
            payload['desc'] = description
        if repeat is not None:
            payload['repeat'] = repeat
        if break_duration is not None:
            payload['beam_break_duration'] = break_duration
        if playlist_string is not None:
            payload['playlist'] = pl

        return payload


def main(args_in):

    class SmartFormatter(argparse.HelpFormatter):
        """Used to nicely format some of the help messages"""
        def _split_lines(self, text, width):
            if text.startswith('R|'):
                return text[2:].splitlines()
                # this is the RawTextHelpFormatter._split_lines
            return argparse.HelpFormatter._split_lines(self, text, width)

    API_OPS = {
        'c': 'create',
        'r': 'read',
        'u': 'update',
        'd': 'delete'
    }

    type_help = '\n'.join('{}: {}'.format(k, v) for k, v in API_OPS.items())

    parser = argparse.ArgumentParser(
        description='Interact with Linear Playlist API',
        formatter_class=SmartFormatter)

    parser.add_argument(metavar='operation',
                        dest='api_op',
                        help='R|Which API operation to perform on linear playlist:\n{}'.format(type_help),
                        choices=list(API_OPS.keys()))

    parser.add_argument(metavar='Playlist ID',
                        dest='plid',
                        nargs='?',
                        help='The ID of the playlist object you want to generate a URL for')

    parser.add_argument('-d', '--desc',
                        default=None,
                        help='Description of playlist being created')

    parser.add_argument('-r', '--repeat',
                        default=None,
                        help='Number of times playlist should repeat (-1 means infinite)')

    parser.add_argument('-t', '--skiptoken',
                        default=None,
                        help='Whether or not to require a signed token for playback (0 is required  or 1 is not '
                             'required) - Listed as "skip_drm" when reading object - 0 by default')

    parser.add_argument('-s', '--addslatefill',
                        default=None,
                        help='Should breaks be filled with ad slate when ads are not available (0 or 1) 0 by default')

    parser.add_argument('-a', '--active',
                        default=None,
                        help='Should the playlist be active or inactive (0 or 1) 1 by default, inactive playlists '
                             'cannot be played back')

    parser.add_argument('-m', '--drm',
                        default=None,
                        help='Should the playlist require studio drm (widevine/playready/fairplay) for playback '
                             '(0 or 1) 0 by default')

    parser.add_argument('-b', '--breakdur',
                        default=None,
                        help='Duration to request for ad breaks within assets in the playlist')

    parser.add_argument('-p', '--playlist',
                        default=None,
                        help='comma separated list of beams and int durations for breaks that represent a playlist.  '
                             'ex: 30,id,id,30,id (used by create/update)')

    if len(args_in) == 0:
        # print out the help
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(args_in)

    pl_api = LinearPlaylistAPI()
    plid = None
    if args.plid:
        plid = args.plid
    if args.api_op == 'c':
        new_list_id = pl_api.create_linear_playlist(args.playlist, args.desc, args.repeat, args.breakdur,
                                                    args.skiptoken, args.addslatefill, args.active, args.drm)
        if new_list_id:
            signer = Signer('https://content.uplynk.com/playlist', 'm3u8', new_list_id)
            signer.gen_playback_url()
            signer = Signer('https://content.uplynk.com/playlist', 'mpd', new_list_id)
            signer.gen_playback_url()
    elif args.api_op == 'r':
        pl_api.list_linear_playlist(plid=plid)
    elif args.api_op == 'u':
        pl_api.update_linear_playlist(plid, args.playlist, args.desc, args.repeat, args.breakdur,
                                      args.skiptoken, args.addslatefill, args.active, args.drm)
    elif args.api_op == 'd':
        pl_api.delete_linear_playlist(plid=plid)
    else:
        print('Unknown API operation: {}'.format(args.api_op))
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
