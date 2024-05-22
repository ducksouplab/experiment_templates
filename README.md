# Experiment

## Installation

Check the steps defined in `_docker/Dockerfile.build`

Install js dependencies:
```
yarn
```

Build JS assets before pushing:
```
make buildfront
```

## Run

Run devserver with (check package.json to see the dev password):

```
make dev
```

If you have an "otree: not found" error, please run:

```
pip3 install -r requirements.txt && pip3 install -U python-dotenv
```

The following environment variables may be used to modify how (all) experiments interact with DuckSoup (here with the default values):

```
OTREE_DUCKSOUP_URL=http://localhost:8000
OTREE_DUCKSOUP_REQUEST_GPU=false
OTREE_DUCKSOUP_FRAMERATE=30
OTREE_DUCKSOUP_WIDTH=800
OTREE_DUCKSOUP_HEIGHT=600
OTREE_DUCKSOUP_FORMAT=H264
```

You may declare in a `.env` file at the root of the project  (copy the provided `env.example` file), or define them in the commandline:

```
DUCKSOUP_URL=https://localhost:8001 make dev
# without make
DUCKSOUP_URL=https://localhost:8001 otree devserver
```

## Build docker image

Build and tag docker image:
```
docker build -f _docker/Dockerfile.build -t experiment_templates:latest .
docker tag experiment_templates ducksouplab/experiment_templates
```

Or 
```
make dockerbuild
```

## Share image

Deploy image to docker hub
```
docker push ducksouplab/experiment_templates:latest
```

Or 
```
make dockerpush
```

Run with docker (and default port)
```
docker run -p 8180:8180 --env DUCKSOUP_URL=https://ducksoup.example.dev --rm experiment_templates:latest
```

if you are using macos use the --platform linux/amd64 flag:
docker run -p 8180:8180 --platform linux/amd64 --env DUCKSOUP_URL=https://ducksoup.example.dev --rm experiment_templates:latest

Check if `FORWARDED_ALLOW_IPS` is needed depending on Docker image / http proxy setup.

## Front-end

Each times the JS sources in `_front/src` are modified, it's necessary to:

```
make buildfront
```

Which will:

- delete old JS processed files in `_static/global/scripts`
- create new ones with esbuild, with hashes appended to their name (for instance `_static/global/scripts/player-S2O2LUA6.js`) (if source is not modified, hash remains the same)
- edit [Templates].Html files to replace hashes in `<script src="..." />` tags

## Deployment

Push on the `container` branch to tag them for futures deployments.

## Controlling player behaviour depending on image resolution

In the experiment `Interact.html` you need to add `listeners.js` (see for instance `ducksoup_now/Interact.html`) plus an optional custom JS script that will do something like:

```js
// this callback is called at start AND when the value changes
// see ducksoup_now.js for an example
window.addWidthThresholdListener((ok) => {
  if(ok) {
    // do something when quality is OK
  } else {
    // do something else when quality is NOT OK
  }
});
```

To enable it you will also need to add in the experiment `__init__.py`, under `Interact#js_vars`:

```python
embedOptions=dict(
  debug=True,
  stats=True, # TODO: enable stats
),
listenerOptions=dict(
  widthThreshold=800, # TODO: define a minimal width for quality to be ok
),
xpOptions=dict(
  alpha=1.0, # TODO: possibly pass extra parameters for your custom script
)
```

And don't forget to build JS assets:

```sh
make buildfront
```