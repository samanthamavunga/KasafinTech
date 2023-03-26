# myApp
The whole project is about building a voice enabled financial management system for smaller businesses
In this example, we've added a new function called create_voice_transcripts_table which creates a new table called "voice_transcripts" with columns for the ID of the user who recorded the voice, the actual transcript text, and the date the transcript was created.

We've also added a new function called store_voice_transcript which takes in the user ID and transcript text as arguments and inserts them into the "voice_transcripts" table.

Finally, we've added a new route called "/store-voice-data" which handles requests to store new voice transcript data. This route expects the transcript text to be included in the request as a form field called "voice_transcript". When a request is received, the route gets the user ID from the session (assuming the user is logged in), stores the voice transcript in the database using the store_voice_transcript function, and returns a success response to the client.

# Prerequisites
- Apache XAMMP running

# Setup project

#  1. Create virtual environment
```bash
python -m venv myenv
```

# 2 . Activate virtual environment
```bash
source myenv/Script/activate
```
# 3 . Install packages
```bash
pip install -r requirements.txt

```
# 4. Run the app
```bash
flask run 
```

# 5. Visit the app in the url
```bash
localhost:5000
```


### Note
Always do `pip freeze > requirements.txt` after installing new packages

```bash
git checkout -b feat/idaya
```


```bash
git checkout -b feat/sam

```
## Add your changes 

```bash 
git add .
git commit -m "update feat/idaya"
git push origin feat/idaya
```


```bash 
git add .
git commit -m "update feat/sam"
git push origin feat/sam
```
```
git checkout main
git pull origin main
git checkout my-branch
git merge main
git commit
git push origin my-branch
Create a pull request to merge your changes from your branch into the main branch. You can do this on the GitHub website by selecting "New pull request" and choosing your branch as the "compare" branch and the main branch as the "base" branch. Once the pull request is created, other contributors can review and approve the changes before they are merged into the main branch.


Ensure that your local main branch is up-to-date with the latest changes from the remote main branch. You can do this by checking out the main branch (git checkout main) and pulling the latest changes from the remote repository (git pull origin main).

Check out your branch (git checkout your-branch).

Merge the latest changes from the main branch into your branch using the following command: git merge main. This will apply any changes made to the main branch since the last time you pulled to your branch.

Resolve any merge conflicts that may arise during the merge process. You can do this by manually editing the affected files and resolving any conflicting changes. Once you've resolved the conflicts, save the changes and commit them using git commit.

Push the changes to the remote repository using the following command: git push origin your-branch. This will update your branch on GitHub with the latest changes from the main branch.


Go to your repository on GitHub and navigate to your branch.

Click on the "Pull request" button.

Click on the "Switch base" button. This will allow you to choose the branch you want to merge into your current branch.

Select "main" as the base branch and your current branch as the compare branch.

Click on the "Create pull request" button. This will create a new pull request that will merge the changes from the main branch into your current branch.

If there are any merge conflicts, GitHub will automatically notify you and provide options to resolve the conflicts. Follow the instructions provided by GitHub to resolve any conflicts and complete the merge.

Once the merge is complete, your branch will be updated with the latest changes from the main branch. 

```