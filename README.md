# indieMachine

**Demonstration:** [My own blog](http://prayag.hudsons.network/blog/), for which I made this whole thing. I hope to expand this engine beyond just my blog, into something that anybody can use the way they want, while already implementing all the features a blog would need to have.

## What is this?

indieMachine is inspired by the IndieWeb movement, and my own dissatisfaction with template-based blogging services. Right now, indieMachine is a barebones blogging engine, with just the core essentials of a blog, to allow the peculiar, particular, and tech-savvy to create their own custom front-end faces to the world without being restricted by templates. I wanted to create a personal blog with a front-end that's written with straight-up scripting, so that I can create an interface that I can change and make more powerful at will; so I wanted to share this hoping that other people out there might want the same, and could make their own beautiful front-ends that make the Web feel more interesting.

In the future, I want this to become a complete web presence and social networking solution, acting as a "machine" that allows you to create posts, cross-post them to free-API or federated social networks (like Mastodon, Tumblr, and Bluesky), and then backfeed replies and reactions back to your blog, with all of that action stationed in one place: your own personal website, a node on the Web that stands strong independently while also being able to interface with any other website, seamlessly, and with a LOT of technological compatibility.

That's just my ambitious long-term goals, though. For now, this blogging engine is more like *half* a blog, which in a way is the point of it.

## What does it support, and what's planned for the future?

- [x] Posts, categories, and comments
  - Front-end idea: your front-end CGI can check posts' categories to display them in different ways, e.g. text-based posts look normal, media-centric posts can have a slideshow/carousel (like with a "Photo" or "Video" category), microposts can have larger text/full-viewport media (like with a "Micropost", "Reel", or "Short" category)
- [x] Limited RSS support (this engine was structured around RSS)
- [x] Limited metaWeblog API support
- [ ] Complete RSS/Atom support
  - [ ] Also the ability to generate RSS feeds for specific categories (via GET form)
- [ ] Complete XML-RPC API (Blogger/metaWeblog/MovableType/WordPress) support
  - [ ] Including closer-to-standard behavior for categories
- [ ] AtomPub, MicroPub support
- [ ] ActivityPub support
- [ ] Cross-posting and backfeeding functionality
- [ ] Functionality for email-based verification and editing of comments (*very*-long-term goal)
- [ ] Bundled template Python CGI, to demonstrate how a front-end can be coded
- [ ] Cleaner, more secure user experience
  - [ ] Configuration file (or whatever is the most secure way to store usernames and passwords and stuff)
    - This will also allow the Python files to be unchained from certain directory structure requirements that I haven't been able to clean up yet. Gotta have more, *more* flexibility!
  - [ ] Verification that the scripts are safe from SQL injection, XML bombs, and other vulnerabilities I may not be aware of
  - [ ] Automated web-based setup
  - [ ] Web-based editing and configuration interface
  - [ ] Cleaner comments in each Python file (maybe follow some kind of commenting convention, like documentation comments)
- [ ] Ability to export/import blog data in a widely-compatible format (maybe a format WordPress uses?)

### Client compatibility

#### Editing

- [x] Windows Live Writer (used as benchmark)
- [ ] MarsEdit (only tested in a limited capacity)
- [ ] (need more clients to test!)

#### Syndication (RSS, etc.)

- [x] NetNewsWire
- [ ] (need more clients to test!)

## How do I use it?

"Installing" the engine is as simple as dragging and dropping these files and folders into the desired web-facing folder on your server...well, it's *almost* that easy. Before the CGI scripts can start working, there are several things you need to do first. (A goal for this project is to have drag-and-drop ease of use, but having all this tedious manual configuration defeats the point, so that's definitely something I'll be working out as I expand on this blog engine.)

### 1. Install the necessary software

Before you start dragging and dropping things, make sure your server is prepared for web hosting! You'll need to install the latest versions of:

- A web server, like NGinX or Apache
- A MySQL-compatible database server, like MariaDB or Oracle's MySQL
- Python
- Additional required Python libraries:
  - dateutil
  - mysql-connector-python
  - defusedxml

### 2. Create the database for the blog

The blog engine requires the latest version of a MySQL-compatible database server. That includes Oracle's MySQL and the open-source MariaDB. I used MariaDB when developing this, but things should work the exact same with MySQL too.

Create a database for your blog. You can call it whatever you'd like (perhaps "indiemachine"?), just make sure you note its name down for later. Then, enter the database and create three tables using these commands:

- **Posts table:** `CREATE TABLE posts (postid INT AUTO_INCREMENT, title TINYTEXT, description TEXT, pubDate DATETIME DEFAULT CURRENT_TIMESTAMP, editDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, setDate DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (postid));`
- **Categories table:** `CREATE TABLE categories (category TINYTEXT, postid INT);`
- **Comments table:** `CREATE TABLE comments (id INT AUTO_INCREMENT, postid INT, name TINYTEXT, webURL VARCHAR(2083), comment TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id));`

Also! Make sure you have a database user with *password access* to the database. If you don't have one, make one. Note down its username and password, too.

### 3. Modify the Python files with your configuration information

This is the step where you need to get your hands dirty (apologies in advance for the cursing in the comments...). Ideally there ought to be a .conf file or something similar (potentially more secure than just a file), but for now everything needs to be entered manually. To make things easier, I placed a prominent `***FILL THIS IN***` string for all the areas that need modification, so you can Control-F your way through each file to modify everything.

Here's what you need to put for each area:

- First of all, the four lines below every `db = mysql.connector.connect(` line are for your MySQL connection information. You'll need to repeat this information three times, once for each Python file.
  - `host=` is the address where you can access your MySQL server. This can be a URL, IP address, or just `localhost` if your web server and MySQL server are on the same computer. (I have only confirmed `localhost` to work, so I don't know whether or not the other two options, i.e. a remote database, work fine. They probably do though, as long as they allow password access.)
  - `user=` is that username I asked you to note down earlier.
  - `password=` is the same deal, it's the password for that user.
  - `database=` is the database name I asked you to note down. It's the one you came up with yourself, unless you just copied "indiemachine".
- Besides that, each Python script has its own parameters to fill in.
  - **edit/index.py:**
    - `blogroot=` is the absolute directory leading to the folder of your blog. This can be directly inside of a virtual host, or it can be in a folder *inside* of that. For example, `/var/www/<vhostfolder>/blog/`, or the like.
    - `blogwebroot=` is the actual web address of your blog, the one that you enter into a web browser. Something like `https://<www.domainname.com>/blog/`. (NOTE: These scripts were written with the expectation that your posts will be shown at the root of your blog, so you can't have a separate `/blog/` main page and then a `/blog/post/index.py` script for post-viewing. That's a limitation that will likely get fixed once a .conf file gets implemented.)
    - `methodCall["params"][userPos] ==` and `methodCall["params"][passPos] ==` are neat. At the moment, you can *only* edit your blog using blogging software, like Open Live Writer or MarsEdit. These two values are your username and password respectively, the ones you'll enter into the blogging software. They're different from your MySQL credentials, so you can make them up! There are no rules on how you should write them, though I'd recommend making sure your password is secure nevertheless. Don't put "a" as the password just because you can 😨
  - **comment/index.py:**
    - `Location:` is the folder of your blog. Take the `blogwebroot` from earlier, and then lop off the domain (e.g. turning `https://<domainname>/blog/` into just `/blog/`). When you create your front-end, the expectation is that your comment box will be a POST form which submits to "/comment/", and then that comment script will immediately redirect back to the post page, showing the newly-added comment.
  - **subscribe/rss/index.py**
    - There's a LOT to fill in here, but fortunately this is where you can have some fun. This script creates an RSS feed for blog visitors to follow, so you're basically just describing your blog! Each `***FILL THIS IN***` line (stopping before the MySQL credentials) has a line above it with a little bit of text telling you what to put, like `"title"` or `"description"`. These are RSS <channel> tag names. The RSS specification can tell you what to put for each field.
    - Other than that, there's one `***FILL THIS IN***` that comes after the MySQL credentials, but that's just your `blogwebroot` again.

### 4. Enable CGI, and give the necessary permissions to different files and folders

*Now* you can do that dragging-and-dropping. At the moment, it's recommended to maintain the structure of the files, i.e. leaving each script inside its respective folder, keeping rsd.xml and all the folders at the same directory level, and also creating a `Graphics/media/` folder to store media. (Again, that .conf file...it'll be revolutionary.)

Your CGI files likely still won't work yet though. I don't know how things work for NGinX and other web servers, but at lesat for Apache (likely applies to other servers too) you need to do a few things:
- Enable CGI support. In Apache, this simply means doing `sudo a2enmod cgi`.
- Configure Apache to recognize ".py" files as CGI scripts. You can do this in such a way that you don't need to be restricted to a "cgi-bin" folder. This means opening Apache's config file (`/etc/apache2/apache2.conf` on Ubuntu Server) and adding these lines:

`<Directory "<blogroot>">`<br>
`  Options +ExecCGI`<br>
`  AddHandler cgi-script .py`<br>
`</Directory>`

- Configure your virtual host to recognize "index.py" as an index file. This means going into its config file (under `/etc/apache2/sites-available/` on Ubuntu Server) and adding "index.py" to the "DirectoryIndex" directive.
- Go back to your blog's folder, and give execute permissions to every "index.py" file, as well as write permissions to specifically `Graphics/media`. That way, your web server will actually be able to run the scripts and write in your media uploads (images and other media that are uploaded through your blogging client).
- Reload the Apache configuration so that it recognizes the configuration changes (this is `sudo systemctl reload apache2` on Ubuntu Server, which if you haven't picked up is the only platform I'm using and testing this on, so I'd need to hear from others how things work on different platforms).

### 5. Set up TLS

This is SUPER-IMPORTANT. You wouldn't want your editing endpoint to be insecure, that's where your password gets sent!! TLS setups can vary, but for a good basic setup, I'd recommend [just getting Let's Encrypt certificates through Certbot](https://certbot.eff.org/instructions).

### 6. Write the front-end you want, in the language you prefer

This setup guide has already been really exhausting to write so far 😅 If you're able to read the code in the scripts, as well as look up documentation for the above-mentioned metaWeblog API, you'll likely be able to easily figure out what you need to write in your scripts. All you'd really need is a single CGI script or PHP file that can read form data, access the MySQL databases to get and display post data, and have an HTML form that sends a POST request to the `/comment/` endpoint.

I would like for this blogging engine to be something that a lot more people can figure out and use, so this is something that I'll have to work on for a future indieMachine release. A full-on tutorial for HTML, CSS, Python, MySQL, and HTTP might be a bit too much, so I may make some kind of cut-and-paste "theme maker" file that has all the necessary code bits you'd need, as well as an explanation and demonstration of how to use them. There's also those other quality-of-life additions that really ought to be basic for a blog engine meant to be used by lots of people, like a web admin interface (yup, you can't edit posts via your web browser right now, you'd literally *need* a separate app). It's all stuff to await for the future.
