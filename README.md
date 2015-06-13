# Project JARVIS
A home enhancement project.

## Previous attempts
- [https://github.com/debugger22/Jarvis](https://github.com/debugger22/Jarvis)
- [https://jasperproject.github.io/](https://jasperproject.github.io/)

## Potentially useful libraries
- Python interface to Google speech to text API [https://pypi.python.org/pypi/SpeechRecognition/](https://pypi.python.org/pypi/SpeechRecognition/)
- Kaldi. Deep neural nets for speech recognition. Open source, Apache License.  
## System Overview

### Input
Jarvis will have rich multi-sensory input, including, but not limited to:

1. Speech
2. Sensors from connected devices
3. Video

These are listed in the order of priority for development. We address speech input more explicitly since it is our first priority.

#### Speech
Requirements for the speech ingestion system for Jarvis:
- Always listening (while Jarvis is running of course)
- Handles multi-microphone input and distinguishes between mics
- Real-time, low latency.

We propose two stages to the speech ingestion system: capture and recognition.

##### Speech: Capture
Proposed interface:
* **Input**: raw audio
* **Output**: mic ID and batched segments of speech data, properly delimited

It might be a good idea to have weak processors locally attached to each microphone that can continuously monitor the input and decide when it is receiving human speech (as opposed to, say, the train going by) and send out the batched segments of speech data over the network to a more powerful processor. The alternative is to have the powerful processor itself handle the incoming raw audio from all microphones. However, this seems less scalable and inefficient.

Potentially useful hardware:
- [Audio Shield for Arduino](http://www.smarthome.com/velleman-vma02-audio-shield-for-arduino.html)
- [Wall mount microphone](http://www.surveillance-video.com/audio-stw1-w5.html/?gclid=CjwKEAjwwN-rBRD-oMzT6aO_wGwSJABwEIkJr4_ISFNwj9OEBkvvbS6BR25CU8VlgqEbGZqyzxtgYRoCCrvw_wcB)

Useful information:
- [Raspberry Pi and real-time low latency audio](http://wiki.linuxaudio.org/wiki/raspberrypi)

###### Speech: Recognition
Proposed interface:
* **Input**: mic ID and batched segments of speech data, delimited
* **Output**: text transcription of the audio data and mic ID

The simplest approach for this module is to simply combine all of the incoming batches of audio data and send it off to some external speech recognition API and use the response. Naturally there are some concerns about this approach: 

- Will latency be an issue?
- What if the audio data is too long for the API?

As long as we keep the interface fixed, we can switch out the recognition system easily enough. To address privacy and latency concerns, it would be great to have a speech recognition system that runs in-house.

Some candidate speech recognition APIs:
- [Google Speech API](https://github.com/gillesdemey/google-speech-v2/). Unfortunately, not officially supported by Google and technically could be dropped at any time. There is a light Python library for it available [here](https://github.com/Uberi/speech_recognition).
- [API.ai](http://api.ai/). This actually includes more than just speech recogntion; it's an entire infrastructure to generate *intents*.

#### Sensors
Left blank for now.

#### Video
Intentionally left blank.

### Processing

#### Natural Language Understanding Module
For now we may use API.ai as an integrated solution for speech recognition and natural language understanding, but eventually we will have an in-house system in place for this.

#### Visual Understanding Module
To be determined.

### JARVIS State
The central component of context and persistence will be what is known simply as the Jarvis State. Essentially, it is a server tasked with rapidly responding to various queries about Jarvis's internal state, enabling updates to the state, and properly managing knowledge vs. ignorance. We'll dive a little deeper into each of these points within this section.

Core requirements for Jarvis STATE:
- Allow external system to query for `state` of some particular `tag`
- Allow updates to state of a `tag`
- Be modular and easily extensible to track states of new elements of the environment

#### Implementation Suggestions
- Support both discrete and continuous values as a **state**. For example, *Lights1* can be ON or OFF, but *OrientationOfTonyStark* is probably a real-valued quaternion.
- Use a lightweight in-memory key-value store, such as [RocksDB](http://rocksdb.org/), [Redis](http://redis.io/), or [Memcached](http://memcached.org/).
- Types of values for a state should probably include:
    - discrete, unordered
    - discrete, ordinal
    - continuous, scalar
    - continous, vector
    - continous, matrix
- Allow any value to be set to *UNKNOWN*

#### Other ideas
Tags don't have to simply be strings such as *Lights1* or *OrientationOfTonyStark*. It might be more useful to have distributed representations of the tags. In other words, we should be able to tell that *Coffee Maker* is very similar to *Tea Kettle* and not very similar to *Projector*. If I make the query

> Is the coffee maker running?

Then I might get the response:

> No, but the tea kettle is on.

This kind of response requires knowledge of what the tags mean and how they are related. A starting point for this might be to use distributed word vectors and a recursive neural net with a single set of tied weights to create the distributed representation of these tags.

All together, each element of the JARVIS state representation could be a triple:

    (tag, distributedRepresentation, value)


### Output
Jarvis may initiate actions that influence the external world, such as turning on the lights, playing music, starting the coffee maker, locking the door, etc. It'll be useful to have a common approach to managing and performing these actions. For this, we will have two core abstractions: the Task Manager, and the Action Driver.

#### Task Manager
A task manager serves as a final bouncer before initiating an action. It fields an action request and fills in any missing data using the JARVIS State, makes sure it's okay to launch this action at this time, then hands all of the information to a driver for that particular action.

There will be multiple task managers, perhaps each handling a family of related actions. Drivers must be registered with the appropriate task manager.


#### Action Driver
An action driver is a stateless module which will take in the launch request from the task manager and handle all the low level details of communicating with any and all physical devices or other services involved in fielding the request. For example, it might adhere to the communication protocol for controlling the Philips Hue lightbulbs. It also returns a status message to the task manager (which actually, might be more helpful to go directly to Jarvis State, but might be a lot for that system to handle).