# Creating Your First DuckSoup Experiment

Welcome to the Simple Chat tutorial! In this guide, you'll learn how to create a basic video chat experiment where two participants can have a conversation and rate their experience. This is a great starting point for understanding how DuckSoup and oTree work together.

## What is oTree?

oTree is an open-source platform for creating and running behavioral experiments and surveys. It allows researchers to build interactive applications using Python, making it easy to design experiments that involve multiple participants. In this repository, oTree is used to orchestrate participants, and collect behavioral data. We use DuckSoup as a plugin inside otree to enable real-time video interactions between participants, as well as the use of real-time audio and video effects. For more in-depth familiarization with oTree, check out their [tutorials](https://otree.readthedocs.io/en/latest/tutorial/intro.html), they are very nice and comprehensive.

> **Quick Start**: All the files discussed in this tutorial are already available in the `simple_chat` folder. You can:
> - Use them directly as a template for your own experiments
> - Follow this tutorial to understand how everything works
> - Mix and match - read the parts you need and copy the rest

## Before You Begin

Make sure you've completed the [DuckSoup and oTree Setup](tutorial.md). You'll need:
- Docker and VSCode installed
- Development environment set up
- DuckSoup and oTree configured and running
- Basic familiarity with the example experiments

Haven't done this yet? No problem! Head over to the [setup tutorial](tutorial.md) first.

## Overview of the Experiment

Let's start with what we're building:

**What participants will experience:**
1. They arrive at the experiment and see instructions
2. They set up their camera and microphone
3. They wait for a partner
4. They have a 3-minute video chat
5. They rate their interaction
6. They see a thank you message

**What we need to create:**
- Main experiment logic (`__init__.py`)
- Rating page template (`Rating.html`)
- Thank you page template (`ThankYou.html`)
- Experiment configuration in `settings.py`

## Setting Up the Experiment

First, let's register our experiment in `settings.py`. Add this to the `SESSION_CONFIGS` list:

```python
dict(
    id='SC',  # Unique identifier
    name='simple_chat',
    display_name='Simple Chat',
    app_sequence=['simple_chat'],
    num_demo_participants=2,
    num_participants_allowed=[2],
    doc="A simple video chat experiment where two participants interact."
),
```

This tells oTree about our experiment and its basic requirements.

## Building the Experiment Logic

Now let's create our main experiment file. We'll break it down into manageable pieces:

### The Foundation: Imports and Constants

In `simple_chat/__init__.py`, we start with our basic setup:

```python
from otree.api import *
import sys
sys.path.append("..")
from config import Env
from _lib.pages import *

# How long each part of the experiment takes
CONNECTING_DURATION = 10    # Time for initial connection
INTERACTION_DURATION = 180  # Length of video chat (3 minutes)
TIMEOUT = 18               # Buffer for network delays
```

### Defining Our Experiment Structure

Next, we set up the basic structure:

```python
class C(BaseConstants):
    NAME_IN_URL = 'simple_chat'
    PLAYERS_PER_GROUP = 2  # We need exactly 2 participants
    NUM_ROUNDS = 1         # One conversation per pair
```

### Tracking Participant Information

The `Player` class is where we define what information we want to collect:

```python
class Player(BasePlayer):
    # Basic information
    sid = models.StringField()        # Session ID
    user_id = models.StringField()    # p1 or p2
    other_id = models.StringField()   # Partner's ID
    dyad = models.StringField()       # Pair identifier
    primary = models.BooleanField()   # Special role for p1
    
    # Device settings from the setup page
    audio_source_id = models.StringField()
    video_source_id = models.StringField()
    
    # Ratings after the conversation
    liked = models.IntegerField(
        label="How much did you like interacting with your partner?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect
    )
    conversation_quality = models.IntegerField(
        label="How would you rate the quality of your conversation?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect
    )
    video_conf_quality = models.IntegerField(
        label="How would you rate the technical quality of the video conference?",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect
    )
    interaction_comment = models.LongStringField(
        label="Do you have any additional comments about your interaction?",
        blank=True
    )
```

### Managing Participants

When a new session starts, we need to set up our participant pairs:

```python
def creating_session(subsession):
    # Create pairs of participants
    subsession.group_randomly(fixed_id_in_group=True)
    
    for player in subsession.get_players():
        # Give each participant an ID (p1 or p2)
        player.user_id = f'p{player.id_in_group}'
        player.sid = subsession.session.config['id']
        
        # Set up their display name
        if not player.participant.label:
            player.participant.label = player.user_id
            
        # Connect them with their partner
        other = player.get_others_in_group()[0]
        player.other_id = f'p{other.id_in_group}'
        player.dyad = 'p1-p2'
        
        # p1 gets some special responsibilities
        player.primary = player.id_in_group == 1
```

### Creating the Video Chat Page

The heart of our experiment is the video chat. Here's how we set it up:

```python
class Interact(Page):
    timeout_seconds = INTERACTION_DURATION + TIMEOUT

    def js_vars(player):
        # Create a unique room name for this pair
        namespace = player.sid
        interaction_name = f'1-{player.dyad}'

        return dict(
            # How long each phase lasts
            connectingDuration=CONNECTING_DURATION,
            interactionDuration=INTERACTION_DURATION,
            
            # DuckSoup connection settings
            playerOptions=dict(
                ducksoupURL=Env.DUCKSOUP_URL,
            ),
            
            # Video chat settings
            peerOptions=dict(
                namespace=namespace,
                interactionName=interaction_name,
                size=2,
                userId=player.user_id,
                
                # Video settings
                gpu=Env.DUCKSOUP_REQUEST_GPU,
                videoFormat=Env.DUCKSOUP_FORMAT,
                width=Env.DUCKSOUP_WIDTH,
                height=Env.DUCKSOUP_HEIGHT,
                frameRate=Env.DUCKSOUP_FRAMERATE,
                
                # Use the devices they selected
                audio=dict(
                    deviceId=dict(
                        ideal=player.participant.audio_source_id
                    ),
                ),
                video=dict(
                    deviceId=dict(
                        ideal=player.participant.video_source_id
                    ),
                    facingMode=dict(ideal="user"),
                ),
            ),
        )
```

### Collecting Feedback

After the video chat, we collect ratings:

```python
class Rating(Page):
    template_name = 'simple_chat/Rating.html'
    form_model = 'player'
    form_fields = ['liked', 'conversation_quality', 
                  'video_conf_quality', 'interaction_comment']
```

The template creates a clean, professional-looking form with our rating questions.

### Finishing Up

Finally, we show a thank you message:

```python
class ThankYou(Page):
    template_name = 'simple_chat/ThankYou.html'
```

And we define the order of pages:

```python
page_sequence = [
    BaseIntroduction,  # Instructions
    BaseSettings,      # Device setup
    BaseWaitForAll,   # Wait for partner
    Interact,         # Video chat
    Rating,           # Feedback
    ThankYou          # Goodbye
]
```

## Testing Your Experiment

Ready to try it out? Here's what to do:

1. Start DuckSoup:
```bash
docker run --name ducksoup_1 -p 8101:8100 -e DUCKSOUP_TEST_LOGIN=admin -e DUCKSOUP_TEST_PASSWORD=admin -e DUCKSOUP_NVCODEC=false -e DUCKSOUP_NVCUDA=false -e GST_DEBUG=3 -e DUCKSOUP_ALLOWED_WS_ORIGINS=http://localhost:8180 -e DUCKSOUP_JITTER_BUFFER=250 -e DUCKSOUP_GENERATE_PLOTS=true -e DUCKSOUP_GENERATE_TWCC=true -v $(pwd)/plugins:/app/plugins:ro -v $(pwd)/data:/app/data -v $(pwd)/log:/app/log --rm ducksoup:latest
```

2. Start oTree:
```bash
make dev
```

3. Run a test:
   - Go to http://localhost:8180/demo
   - Click "Simple Chat"
   - Open two browser windows
   - Try the whole experiment flow

## Troubleshooting

Having issues? Check these common problems:

**Video isn't working?**
- Check browser permissions
- Make sure DuckSoup is running
- Try selecting a different camera in settings

**Can't connect with partner?**
- Both participants need to complete device setup
- Check that DuckSoup is running
- Look for errors in the browser console

**Rating page problems?**
- All rating scales are required
- Comments are optional
- Try refreshing if the form won't submit

## Making It Your Own

Now that you have a working experiment, you might want to:
- Add more questions or surveys
- Change the interaction time
- Customize the look and feel
- Add experimental conditions

## Adding Video Effects

Let's enhance our experiment by adding real-time facial manipulation using DuckSoup's Mozza plugin. We'll make both participants appear to smile more during their interaction.

First, make sure you have the Mozza plugin properly set up in your DuckSoup installation. If you haven't done this yet, follow the [Mozza setup instructions](https://github.com/ducksouplab/ducksoup/blob/main/tutorials/run_in_local.md#incorporate-mozza-to-perform-real-time-smile-manipulation).

Now, let's modify our `Interact` page to include the smile effect. Update the `js_vars` method in your `__init__.py`:

```python
def js_vars(player):
    namespace = player.sid
    interaction_name = f'1-{player.dyad}'

    # Configure the smile effect
    video_fx_name = "video_fx"
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    video_fx = f'mozza alpha=1.2 name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'

    return dict(
        # Previous settings remain the same
        connectingDuration=CONNECTING_DURATION,
        interactionDuration=INTERACTION_DURATION,
        playerOptions=dict(
            ducksoupURL=Env.DUCKSOUP_URL,
        ),
        
        # Video chat settings with added effects
        peerOptions=dict(
            namespace=namespace,
            interactionName=interaction_name,
            size=2,
            userId=player.user_id,
            
            # Add the video effect configuration
            videoFx=video_fx,
            
            # Video settings remain the same
            gpu=Env.DUCKSOUP_REQUEST_GPU,
            videoFormat=Env.DUCKSOUP_FORMAT,
            width=Env.DUCKSOUP_WIDTH,
            height=Env.DUCKSOUP_HEIGHT,
            frameRate=Env.DUCKSOUP_FRAMERATE,
            
            audio=dict(
                deviceId=dict(
                    ideal=player.participant.audio_source_id
                ),
            ),
            video=dict(
                deviceId=dict(
                    ideal=player.participant.video_source_id
                ),
                facingMode=dict(ideal="user"),
            ),
        ),
    )
```

Let's break down the video effect configuration:

1. **Effect Setup**:
   ```python
   video_fx_name = "video_fx"
   mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
   ```
   - Creates a unique identifier for each participant's video stream
   - Ensures effects are applied correctly to each participant

2. **Smile Effect**:
   ```python
   video_fx = f'mozza alpha=1.2 name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
   ```
   - `alpha=1.2`: Controls the intensity of the smile effect (values > 1 increase smile)
   - `deform=plugins/smile10.dfm`: Uses the smile deformation model
   - `beta=0.001`: Fine-tunes the deformation
   - `fc=1.0`: Sets the facial control parameter

3. **Integration**:
   ```python
   peerOptions=dict(
       # ... other options ...
       videoFx=video_fx,
       # ... other options ...
   )
   ```
   - Adds the effect to the video configuration
   - Applied in real-time during the interaction

This configuration will make both participants appear to smile more during their interaction. You can adjust the `alpha` parameter to control the intensity of the effect:
- `alpha=1.2`: Strong smile enhancement
- `alpha=0.8`: Strong Smile reduction

Note: Values greater than 1 increase the smile intensity, while values less than 1 decrease it.

## Adding Audio Effects

You can also modify participants' voices using audio effects. Let's see how to use the pitch plugin to alter voice pitch during the interaction. Update the `js_vars` method in your `__init__.py` to include audio effects (see audio_fx parameter in the peerOptions):

```python
def js_vars(player):
    namespace = player.sid
    interaction_name = f'1-{player.dyad}'

    # Configure the audio effect
    audio_fx = 'pitch pitch=1.2'  # Increases pitch by 20%

    return dict(
        # Previous settings remain the same
        connectingDuration=CONNECTING_DURATION,
        interactionDuration=INTERACTION_DURATION,
        playerOptions=dict(
            ducksoupURL=Env.DUCKSOUP_URL,
        ),
        
        # Video chat settings
        peerOptions=dict(
            namespace=namespace,
            interactionName=interaction_name,
            size=2,
            userId=player.user_id,
            
            # Add the audio effect configuration
            audioFx=audio_fx,
            
            # Standard settings
            gpu=Env.DUCKSOUP_REQUEST_GPU,
            videoFormat=Env.DUCKSOUP_FORMAT,
            width=Env.DUCKSOUP_WIDTH,
            height=Env.DUCKSOUP_HEIGHT,
            frameRate=Env.DUCKSOUP_FRAMERATE,
            
            audio=dict(
                deviceId=dict(
                    ideal=player.participant.audio_source_id
                ),
            ),
            video=dict(
                deviceId=dict(
                    ideal=player.participant.video_source_id
                ),
                facingMode=dict(ideal="user"),
            ),
        ),
    )
```

Let's understand the audio effect configuration:

1. **Pitch Effect**:
   ```python
   audio_fx = 'pitch pitch=1.2'
   ```
   - Uses GStreamer's pitch plugin
   - `pitch=1.2`: Increases pitch by 20%
   - Values > 1 make the voice higher in pitch
   - Values < 1 make the voice lower in pitch

2. **Integration**:
   ```python
   peerOptions=dict(
       # ... other options ...
       audioFx=audio_fx,
       # ... other options ...
   )
   ```
   - Adds the effect to the audio configuration
   - Applied in real-time during the interaction

You can adjust the pitch parameter to achieve different effects:
- `pitch=1.2`: Voice is 20% higher
- `pitch=0.8`: Voice is 20% lower
- `pitch=1.5`: Voice is 50% higher (might sound unnatural)

Note: Keep the pitch values within reasonable ranges (0.8 to 1.4) to maintain intelligible speech.

### Combining Audio and Video Effects

You can use both audio and video effects together. Here's how to combine them:

```python
def js_vars(player):
    namespace = player.sid
    interaction_name = f'1-{player.dyad}'

    # Configure both effects
    video_fx_name = "video_fx"
    mozza_user_id = f'ns-{namespace}-n-{interaction_name}-u-{player.user_id}'
    video_fx = f'mozza alpha=1.2 name={video_fx_name} deform=plugins/smile10.dfm beta=0.001 fc=1.0 user-id={mozza_user_id}'
    audio_fx = 'pitch pitch=1.2'

    return dict(
        # ... other settings ...
        peerOptions=dict(
            # ... other options ...
            videoFx=video_fx,
            audioFx=audio_fx,
            # ... rest of options ...
        ),
    )
```

This configuration will:
1. Enhance participants' smiles by 20%
2. Increase their voice pitch by 20%

Remember to:
1. Test the effects thoroughly before running experiments
2. Consider how the combination of effects might impact interaction
3. Document all effect parameters in your research methods
4. Monitor audio quality during testing

## Testing Your Experiment

Ready to try it out? Here's what to do:

1. Start DuckSoup:
```bash
docker run --name ducksoup_1 -p 8101:8100 -e DUCKSOUP_TEST_LOGIN=admin -e DUCKSOUP_TEST_PASSWORD=admin -e DUCKSOUP_NVCODEC=false -e DUCKSOUP_NVCUDA=false -e GST_DEBUG=3 -e DUCKSOUP_ALLOWED_WS_ORIGINS=http://localhost:8180 -e DUCKSOUP_JITTER_BUFFER=250 -e DUCKSOUP_GENERATE_PLOTS=true -e DUCKSOUP_GENERATE_TWCC=true -v $(pwd)/plugins:/app/plugins:ro -v $(pwd)/data:/app/data -v $(pwd)/log:/app/log --rm ducksoup:latest
```

2. Start oTree:
```bash
make dev
```

3. Run a test:
   - Go to http://localhost:8180/demo
   - Click "Simple Chat"
   - Open two browser windows
   - Try the whole experiment flow

Need help? Check out the other tutorials or ask in the DuckSoup community!

## Moving to More Complex Experiments

Once you have a basic understanding of how to create a simple chat experiment, you may want to explore more complex scenarios involving multiple interactions with different partners. Here are a few examples to guide you:

### Example 1: Within-Participant Designs with Dyads

In a within-participant design, each participant interacts with multiple partners across different rounds. You can achieve this by modifying the `NUM_ROUNDS` constant in your experiment's `__init__.py` file. For instance, if you want each participant to interact with different partners in four rounds, you would set:

```python
class C(BaseConstants):
    NAME_IN_URL = 'dyad_experiment'
    PLAYERS_PER_GROUP = 2  # Each interaction is still a dyad
    NUM_ROUNDS = 4         # Four rounds of interaction
```

You would also need to implement a pairing logic that ensures participants are matched with different partners in each round. This can be done using a pairing matrix such as:

```python
PAIRING = [
    [[1, 2], [3, 4], [5, 6], [7, 8]],  # Round 1 pairs. Participant 1 interacts with participant 2, participant 3 with participant 4, etc.
    [[1, 3], [2, 4], [5, 7], [6, 8]],  # Round 2 pairs. Participant 1 interacts with participant 3, participant 2 with participant 4, etc.
    [[1, 4], [2, 3], [5, 8], [6, 7]],  # Round 3 pairs. Participant 1 interacts with participant 4, participant 2 with participant 3, etc.
    [[1, 5], [2, 6], [3, 7], [4, 8]],  # Round 4 pairs. Participant 1 interacts with participant 5, participant 2 with participant 6, etc.
]
```

### Example 2: Handling Different Manipulations for Each Dyad

In more complex experiments, you may want to apply different manipulations based on the dyad's condition. For instance, you can define conditions such as "Smile" and "No Smile" for each dyad and apply different video effects accordingly.

In your `creating_session` function, you can set conditions for each participant based on their dyad:

```python
def creating_session(subsession):
    # ... existing code ...
    
    for player in subsession.get_players():
        # Assign conditions based on the dyad they are in
        if player.id_in_group == 1:  # Primary participant
            player.participant_condition = 'S'  # Smile effect
        else:  # Secondary participant
            player.participant_condition = 'U'  # No smile effect
```

Similarly, you can create different manipulations for different rounds:

```python
def creating_session(subsession):
    # ... existing code ...
    
    for player in subsession.get_players():
        # Assign conditions based on the round participants are in  
        player.participant_condition = 'S' if player.round_number % 2 == 1 else 'U'  # Smile for odd rounds, no smile for even rounds
```

Alternatively, you can randomize the conditions for each participant:

```python
def creating_session(subsession):
    # ... existing code ...
    
    for player in subsession.get_players():
        # Randomize conditions for each participant based on the round they are in
        player.participant_condition = 'S' if player.round_number % 2 == 1 else 'U'
```

Then, in your `js_vars` method, you can check these conditions to apply the appropriate video effects:

```python
def js_vars(player):
    # ... existing code ...
    
    if player.participant_condition == 'S':
        video_fx = 'mozza alpha=1.2 ...'  # Smile effect for primary
    else:
        video_fx = 'mozza alpha=0.8 ...'  # No smile effect for secondary

    return dict(
        # ... existing settings ...
        peerOptions=dict(
            # ... existing options ...
            videoFx=video_fx,
            # ... other options ...
        ),
    )
```

### Conclusion

By following these examples, you can expand your experiments to include multiple interactions with different partners while applying specific manipulations for each dyad. This allows for a richer exploration of behavioral interactions and the effects of different conditions on participant behavior.

For more detailed guidance on creating complex experiments, refer to the oTree documentation and community resources. 