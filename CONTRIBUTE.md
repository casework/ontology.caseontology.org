# Ontodocs Auto-Deployment

Previously, documentation for new releases of *CASE*/*UCO* would have to be manually built using gendocs/ontodocs, in order to deploy documentation via the project websites ([CASE](https://caseontology.org/)/[UCO](https://unifiedcyberontology.org)). With this repository, building the documentation and deploying it on the web will be a more automated process, and allow for local documentation to be built for necessary cases.


## Directions for generating documentation for a new release

The intended audience for this section is documentation maintainers.


### Warnings

The documentation generation must be carried out on a case-sensitive file system. (macOS's default file system deployment is case-insensitive.)

**Do not** commit changes under the `/case` directory on a case-insensitive file system.  Conflicts due to upper-vs.-lower casing will create erroneous symlink references.  Be aware that changes will be present on a fresh `git clone` in a case-insensitive file system.


### Generation directions

When a new ontology release is created, follow these steps:

1. Update the ontology-tracking submodule pointer in this repository to point at the new release's commit.
2. The version of CASE is hard-coded in `case/Makefile` as part of titling the documentation.  Update it to the new version.
3. Run `make clean`.
4. Run `make`.  (`make -j` will work.)
5. Run `git add case`.  This will pick up all file deletions and new file creations.
6. Commit the changes.
7. Push to Github.
8. Run `git pull` in the deployment space.


## Directions for deployment of this repository as a documentation service

For the deployment of the documentation, we assume this repository is cloned to a Linux server, becoming the directory `/srv/http/ontology.caseontology.org/`. The nginx configuration file and casedocs systemctl service file are pathed to this directory by default.

### Configuration
To deploy, the system will need to have **Nginx** installed and this repository cloned on it. We will use a simple **flask** router and a a series of version-specific mapping files to route traffic to the proper documentation pages. This CONTRIBUTE.md page will outline installing **Nginx** and utilizing the **Makefile** to test the setup. All commands will assume the deployment system is a debian-based system *(such as Ubuntu)*.


First, update the package repositories and update the system:

```bash
$ sudo apt-get update
$ sudo apt-get -y upgrade
```


Then, install Nginx on the server:

```bash
$ sudo apt-get install nginx
```


Create a directory where the CASE autodocs repository will live, and a system user:

```bash
$ sudo mkdir -p /srv/http/ontology.caseontology.org
$ sudo useradd -s /usr/sbin/nologin -r -M -d /srv/http/ontology.caseontology.org casedocs
```


Use the system user to clone this repository on the machine, you will need to initalize a repository in the home directory, to be able to pull to the non-empty target:
```bash
$ sudo su casedocs -s /bin/bash
$ cd /srv/http/ontology.caseontology.org; git init
$ git remote add origin git@github.com:casework/ontology.caseontology.org.git
$ git pull && git checkout main
```


Follow the "General Directions" for building the documentation via gendocs, then proceed to change directories to the `router/` directory, and build the flask router seperately:
```bash
$ cd router/
$ make clean && make
# finally, we can exit back to the root user
$ exit
```


Copy the `casedocs.service` file so that systemctl can use it, reload, and enable the service:

```bash
$ sudo cp /srv/http/ontology.caseontology.org/router/casedocs.service /etc/systemd/system/
$ sudo systemctl daemon-reload
$ sudo systemctl enable casedocs.service
# finally, start the flask router and check the status of it
$ sudo service casedocs start
$ sudo service casedocs status
```


Assuming that the casedocs service starts successfully, you can proceed to move the nginx configuration file to the `sites-enabled` directory and remove the default file:
```bash
$ sudo cp /srv/http/ontology.caseontology.org/router/case.nginx.conf /etc/nginx/sites-enabled/
$ sudo rm /etc/nginx/sites-enabled/default
$ sudo service nginx configtest
$ sudo service nginx restart
```


You should now be able to navigate to the IP address of your system and see the documentation live:
```bash
# to get the IP information
$ ip a s
```

To modify the nginx configuration file and add a hostname, add the following line as follows:
```shell
server {
    listen 80;
    server_name mywebsite.com;

    location /documentation {
        root /srv/ontology.caseontology.org;
        try_files $uri $uri/ /index.html =404;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```



#### Optional Localhost

If you are running the deployment on a system that does not access the internet, or you wish to only provide the documentation locally, you may want to add an entry to your hosts file.

```bash
$ sudo vi /etc/hosts
```



### Debugging

There are a variety of errors that you can face, but we are going to address the most common ones.

**403** - For 403 errors, check to ensure that the permissions are properly set on the folder and files. For this, we will use the example directory `/srv/http/ontology.caseontology.org`:

```bash
$ sudo find /srv/http/ontology.caseontology.org -type d -exec chmod 775 {} \;
$ sudo find /srv/http/ontology.caseontology.org -type f -exec chmod 664 {} \;
$ sudo chown -R casedocs:casedocs /srv/http/ontology.caseontology.org
```

**404** - For 404 errors, is commonly a symptom of the pathing between nginx and the flask router being incorrect:
- Ensure that the paths defined in the systemctl file (`/etc/systemd/system`) are correctly pointing to the router
- Check the nginx configuration file (`/etc/nginx/sites-enabled/`) to ensure that the pathing to the documentation is correct
- Ensure that `default` config for nginx is deleted (no longer in `/etc/nginx/sites-enabled/*`)
- Check that the file actually exists! `tail -f /var/log/nginx/error.log`

**500** - For any 500 errors, the server may be mis-configured, you can check the following areas to see if there is relevant outputs. This is commonly due to `/etc/apache/apache.conf` being mis-configured, or a typo in one of the sites which are enabled.

```bash
$ sudo tail -f /var/log/nginx/error.log
$ journalctl
```


### Testing

To test the deployment, run the **Makefile** to ensure expected URL behaviors and content types.

```bash
$ make check-service
```

If you have set the VirtualHost on apache as anything besides `localhost`, you will want to supply this prefix with the `HOST_PREFIX` parameter.  For example, to test the production service, run:

```bash
$ make HOST_PREFIX=https://ontology.caseontology.org check-service
```

As another example, if you have a local deployment at `https://documentation.intranet.example.org/`, run:

```bash
$ make HOST_PREFIX=https://documentation.intranet.example.org check-service
```
