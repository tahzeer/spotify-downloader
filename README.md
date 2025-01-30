# Spotify Downloader

Python script that allows you to download audio tracks from Spotify by providing a Spotify URL. It utilizes the Spotify and YouTube APIs to retrieve track information and search for corresponding YouTube videos. The YouTube videos are then downloaded and converted to MP3 audio files with their metadata preserved.

## Prerequisites

Before using the script, make sure you have the following prerequisites installed:

- Python 3.1x

## Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/tahzeer/spotify-downloader.git
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Obtain a Spotify API client ID and client secret by creating a new application in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

2. Set the Spotify API credentials as environment variables:

```bash
export SPOTIPY_CLIENT_ID="<your_client_id>"
export SPOTIPY_CLIENT_SECRET="<your_client_secret>"
```

3. Run the script:

```bash
python unspotify.py
```

4. Follow the prompts to authenticate with your Spotify account and select the track/playlist you want to export. Ensure that the playlist selected must be public.

```bash
Spotify URL: <spotify_song_or_playlist_url>
```

6. The script will go through each song in the playlist or throught the song in case of a single track, and download the song(s) in mp3 format with metadata.

7. The exported mp3 files will be saved in the `../music` directory.

## Common Issues and Fixes

### RegexMatchError - ``pytube/cypher.py``

RegexMatchError: get_transform_object: could not find match for var for={(.*?)}

[Fix found on StackOverflow](https://stackoverflow.com/questions/76704097/pytube-exceptions-regexmatcherror-get-transform-object-could-not-find-match-fo)

- In file `.venv/lib/python3.10/site-packages/pytube/cipher.py`. I am using python 3.10 and my virtual environment is called .venv You just have to find the library pytube and go to the file cipher.py and edit its source code for now.
- Find the method `get_transform_object` and replace it as below
```
def get_transform_object(js: str, var: str) -> List[str]:
    pattern = r"var %s={(.*?)};" % re.escape(var)
    logger.debug("getting transform object")
    regex = re.compile(pattern, flags=re.DOTALL)
    transform_match = regex.search(js)
    
    if not transform_match:
        # Commented out the line raising the RegexMatchError
        # raise RegexMatchError(caller="get_transform_object", pattern=pattern)
        logger.error(f"No match found for pattern: {pattern}")
        return []  # Return an empty list if no match is found

    return transform_match.group(1).replace("\n", " ").split(", ")    
```

## Future Plans

- [ ] Improve code readability
- [ ] Imporve CLI readability
- [ ] Skip song if already downloaded
- [ ] Add lyrics file from `genius.com`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. Feel free to clone this repository and use it for personal or educational purposes.
