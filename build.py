#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
import fileinput

'''
This program accepts one optional command line option:

release If provided this will create release ready ZIP files

        Default: 'False'

'''
addonDir = 'Questie'

def main():
    isReleaseBuild = False
    cliVersion = ''
    if len(sys.argv) > 1:
        ver = False
        for arg in sys.argv[1:]:
            if ver:
                cliVersion = arg
                ver = False
            elif arg in ['-r', '--release']:
                isReleaseBuild = True
                print("Creating a release build")
            elif arg in ['-v', '--version']:
                ver = True

    release_dir = get_version_dir(isReleaseBuild, cliVersion)

    if os.path.isdir('releases/%s' % release_dir):
        print("Warning: Folder already exists, removing!")
        shutil.rmtree('releases/%s' % release_dir)

    release_folder_path = 'releases/%s' % release_dir
    release_addon_folder_path = release_folder_path + ('/%s' % addonDir)

    copy_content_to(release_addon_folder_path)

    if cliVersion != '':
        for toc in ['/Questie-BCC.toc', '/Questie-Classic.toc']:
            questie_toc_path = release_addon_folder_path + toc
            with fileinput.FileInput(questie_toc_path, inplace=True) as file:
                for line in file:
                    if line[:10] == '## Version':
                        print('## Version: ' + cliVersion)
                    else:
                        print(line, end='')

    zip_name = '%s-%s' % (addonDir, release_dir)
    zip_release_folder(zip_name, release_dir, addonDir)

    print('New release "%s" created successfully' % release_dir)


def get_version_dir(is_release_build, cliVersion):
    version, nr_of_commits, recent_commit = get_git_information()
    if cliVersion != '':
        version = cliVersion
    print("Tag: " + version)
    if is_release_build:
        release_dir = "%s" % version
    else:
        release_dir = "%s-%s" % (version, recent_commit)

    print("Number of commits since tag: " + nr_of_commits)
    print("Most Recent commit: " + recent_commit)
    branch = get_branch()
    if branch != "master":
        release_dir += "-%s" % branch
    print("Current branch: " + branch)

    return release_dir


directoriesToSkip = ['.git', '.github', '.history', '.idea', '.vscode', 'ExternalScripts(DONOTINCLUDEINRELEASE)', 'releases']
filesToSkip = ['.gitattributes', '.gitignore', '.luacheckrc', 'build.py', 'changelog.py', 'cli.lua', '.DS_Store']


def copy_content_to(release_folder_path):
    for _, directories, files in os.walk('.'):
        for directory in directories:
            if directory not in directoriesToSkip:
                shutil.copytree(directory, '%s/%s' % (release_folder_path, directory))
        for file in files:
            if file not in filesToSkip:
                shutil.copy2(file, '%s/%s' % (release_folder_path, file))
        break


def zip_release_folder(zip_name, version_dir, addon_dir):
    root = os.getcwd()
    os.chdir('releases/%s' % version_dir)
    print("Zipping %s" % zip_name)
    shutil.make_archive(zip_name, "zip", ".", addon_dir)
    os.chdir(root)


def get_git_information():
    if is_tool("git"):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        p = subprocess.check_output(["git", "describe", "--tags", "--long"], cwd=script_dir, stderr=subprocess.STDOUT)
        tag_string = str(p).rstrip("\\n'").lstrip("b'")

        # versiontag (v4.1.1) from git, number of additional commits on top of the tagged object and most recent commit.
        version_tag, nr_of_commits, recent_commit = tag_string.rsplit("-", maxsplit=2)
        recent_commit = recent_commit.lstrip("g")  # There is a "g" before all the commits.
        return version_tag, nr_of_commits, recent_commit
    else:
        raise RuntimeError("Warning: Git not found on the computer, using fallback to get a version.")


def get_branch():
    if is_tool("git"):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # git rev-parse --abbrev-ref HEAD
        p = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=script_dir)
        branch = str(p).rstrip("\\n'").lstrip("b'")
        return branch


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    return shutil.which(name) is not None


if __name__ == "__main__":
    main()
