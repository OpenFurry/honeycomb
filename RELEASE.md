# Release Process

* Ensure that the project is clean across versions by running `make check`
* Tag your release
    * ensure master is up to date: `git pull upstream master`
    * update the revno file: `TAG=<new tag> make update-revno`
    * relying on semver as an outline, make an empty commit specifying the release: `git commit -am "Releasing <new tag>"`
    * tag and sign the release: `git tag -s <new tag>`
* Push the new tag
    * push the changes: `git push upstream master`
    * push the tags: `git push --tags upstream`
