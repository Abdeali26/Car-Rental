# Make sure git is tracking your project.

1. Using your terminal/command line, get inside the folder where your project files are kept: 
  `cd /path/to/my/codebase`. 

  You cannot do this simply by opening the folder normally, you must do this with the command line/terminal. 
  
  Do you need a refresher on using your command line/terminal? [I've compiled my favorite resources here.](http://stackforyourself.com/comp-sci/2016/10/01/command-line/)

2. Check if `git` is already initialized: `git status`

  If you get this error message: `fatal: Not a git repository (or any of the parent directories): .git`, that means the folder you are currently in is not being tracked by `git`. In that case, initialize `git` inside your project folder by typing `git init`, then going through the process of adding and committing your project. 

  If you get another error message, read carefully what it says. Is it saying `git` isn't installed on your computer by saying that the word 'git' is not recognized? Is it saying that you're already in a folder or sub-folder where `git` is initialized? Google your error and/or output to understand it, and to figure out how to fix it.

  Do you need a refresher on `git`? [Go through Codecademy's `git` course.](https://www.codecademy.com/courses/learn-git)

<hr>

# Create a remote, empty folder/repository on Github.

1. Login to your Github account. 

2. At the top right of any Github page, you should see a '+' icon. Click that, then select 'New Repository'. 

3. Give your repository a name--ideally the same name as your local project. If I'm building a travel application, its folder will be called 'travel-app' on my computer, and 'travel-app' will be the Github repository name as well.

4. Click 'Create Repository'. The next screen you see will be important, so don't close it.

<hr>

# Connect your local project folder to your empty folder/repository on Github.

The screen you should be seeing now on Github is titled **'Quick setup — if you’ve done this kind of thing before'**. 

Copy the link in the input right beneath the title, it should look something like this: 
`https://github.com/mindplace/test-repo.git` 
This is the web address that your local folder will use to push its contents to the remote folder on Github.

1. Go back to your project in the terminal/command line. 

2. In your terminal/command line, type `git remote add origin [copied web address]` 

  Example: `git remote add origin https://github.com/mindplace/test-repo.git`

3. Push your branch to Github: `git push origin master` 

4. Go back to the folder/repository screen on Github that you just left, and refresh it. The title **'Quick setup — if you’ve done this kind of thing before'** should disappear, and you should see your files there. 