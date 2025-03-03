# Post-Prescreening Tutorial

This tutorial provides step-by-step guidance for conducting a prescreening experiment using our software with Prolific. **Please note**: The instructions for Mastok sessions and Prolific messages must remain exactly as written (do not modify their text). Below you will find additional context and details organized in a clearer format.

---

## 1. General Information

- **Participant Engagement**: Participants in the prescreening seem more engaged and cognitively available during the actual experiment.
- **Recruitment Size**:
  - Consider recruiting large groups because you will lose at least 20% of participants:
    - Some may not show up.
    - Some may fail the test during the experiment.
  - Alternatively, if Prolific can recruit several participants in parallel (e.g., a large US-based sample), you might opt out of doing a separate prescreening session and revert to an in-study test.
- **Typical Numbers**:
  - You might expect about 10 participants per half-day for the prescreening.
  - Approximately half of these participants pass the test.

---

## 2. Steps for the Prescreening

1. **Locate the Prescreen Code**  
   The code for the prescreen session is in the `technical_prescreen` experiment.

2. **Adjust Dates**  
   Make sure to change the dates accordingly in all the session files before launching.

3. **Push to Production**  
   Push the updated repository to production so the changes are live.

4. **Create a Mastok Session**  
   - Configure it for the prescreening with 1 person per experiment.
   - Set `max sessions = 128`.
   - Allow 24 sessions in parallel.
   - Duration is approximately 5 minutes.

---

## 3. Instructions for the Mastok Session
### 3.1 Consten form

Below is the text for the **Mastok session** to put in your session as consent form. Please change the dates as required.
---

This is a pre-screening experiment for a social interaction experiment in which participants interact in an audio-conference setting with each other. The pre-screening aims to assess that your audio-communication setup is of sufficient quality and compatible with our software.

Furthermore, we would like to record the audio of your voice. These recordings  will remain completely confidential and will only be used for scientific purposes.

TECHNICAL REQUIREMENTS

This experiment only works if you are using the LATEST version of the google CHROME Browser. If you don’t have the latest version of Chrome, please update your software now and come back to this page after updating and restarting it (the browser needs restarting to finish update). Please do not continue if you don’t have the latest version of Chrome. This is very important as it may break the communication with other participants.
	-[ ]	Check this box to confirm that you are using the latest version of the Chrome Browser.

Moreover, we need to ensure that audio-conference communication will happen in the best possible setting. Only continue if you agree and consent with the statements below:
	-[ ] I have a high-quality internet connection.
	-[ ] I have a microphone in my current computer.
	-[ ] I agree to wear headphones (preferably in-ear) during the interactions.
	-[ ] I am in a calm and silent environment.

Consent
	- [ ] By continuing, you declare that you have read and fully understood the paragraphs above, and that you agree to participate in this study. If you don’t consent and don’t want to participate in the study please click on this link to return your prolific submission and close this page.

[accept]Consent[/accept]
[alert]Accepting conditions above is required before starting[/alert]

### 3.2 Paused instructions
We are very sorry, there are no spots left to participate in the experiment at the moment. However, the researcher might still have a place if another participant dropped out. Please send a message to the experimenter as soon as possible if you would still like to participate in the experiment.

### 3.3 Complete instructions

We are very sorry, there are no spots left to participate in this experiment. Please return your Prolific submission by clicking on this link.

### 3.4 Pending message
We are very sorry. To handle server load we can only run a certain number of participants in parallell. Please wait 1 or 2 minutes. If the waiting time exceeds 2 minutes please return your Prolific submission by clicking on this link. You will be compensated for your waiting time, please send us a direct message.


## 4. Preparing a Prolific Session for the Prescreening

Below is the **Prolific message** text to put in your session. Please change the dates as required.

Your Experiment Friday: 10:00 AM GMT
Dear Participant,

Thank you for participating in our study. Your scheduled session for the “Audio-conference multiperson game with other participants” experiment begins at 10:00 AM GMT on friday, 2025-02-28.

Important Details:

The study will appear on your Prolific dashboard at 9:50 AM GMT (10 minutes before start time)

Please be logged in and ready by 9:55 PM GMT (5 minutes before start)

The session will last approximately 60 minutes
You will complete a brief audio test when you join (similar to the pre-screening)
We heard the results from the audio test and saw that some participants were not using headphones and some had a high level of background noise, this drastically diminishes the quality of the recordings. Please make sure to use headphones and be in a clam and silent environment during the experiment.
What to Know:
Your timely participation is crucial as other participants will be waiting.

If the study is not visible on your dashboard at 9:50 AM, please message us immediately for a direct link.

We will send another notification when the study is live on your dashboard.

Thank you for your valuable contribution to our research!
Best regards, The Experiment Team

---

## 5. Running the Actual Experiment

1. **Create a Session**  
   After setting up your Mastok prescreening session, create a corresponding session on Prolific.

2. **Open Mastok Session and Prolific**  
   - Publish the Prolific session **20 minutes before** the scheduled start.
   - Mastok should be open and ready to accept participants.

3. **Monitor Data**  
   - Use the oTree sessions interface to see how many spots are available.
   - If the session is filled or if participants fail the prescreen test, close the Prolific session to prevent over-recruitment.

4. **Recover Prolific IDs**  
   - For each time slot, gather the Prolific IDs of participants who have shown up and passed the prescreen.

5. **Create Participant Group and Send Messages**  
   - Organize participants into groups based on their time slot.
   - Send them the Prolific link or instructions, confirming the time and date.

6. **Monitor Prolific Chat**  
   - Ensure all participants can join without issues.
   - If someone cannot join, provide them with a direct link to Mastok.

7. **Monitor Experiment Progress**  
   - Oversee how participants move through the stages.
   - Follow up if someone drops out or fails the technical requirements.


**End of Tutorial**  
You now have a structured overview of how to set up, run, and monitor a prescreening experiment using Mastok and Prolific. Good luck with your experiment!