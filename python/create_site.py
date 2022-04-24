# Author:  Martin McBride
# Created: 2022-04-16
# Copyright (c) 2022, Martin McBride
# License: MIT

import shutil, os
import pystache
import create_site_structure
import create_site_map

def get_public_path_for_page(public_path, filepath):
    """
    Return the folder and path for a page
    :param public_path: Location for generated files
    :param filepath: html path for this page
    :return:
    """
    directory = os.path.join(public_path, filepath)
    html_name = 'index.html'
    html_path = os.path.join(directory, html_name)
    return directory, html_path

def read_html_template(config):
    """
    Read in the html template from the theme
    :param config: configuration from config.yaml
    :return:
    """
    try:
        theme = config["theme"]
        template_path = os.path.join("themes", theme, "template.html")
        with open(template_path) as infile:
            template = ''.join(infile)
    except Exception as e:
        print("Error reading template file", template_path)
        print(e)
        raise

    return template

def write_webpage(config, html_template, public_path, webpage, site_structure):
    """
    Write the page HTML to the correct place in the output folder, creating any necessary subfolder.
    :param config:
    :param html_template: HTML data for file
    :param public_path: Output folder
    :param webpage: Page information
    :param webpages: All pages
    :return:
    """

    toc = create_site_structure.get_toc_for_webpage(site_structure, webpage)
    webpage["toc"] = toc

    html = pystache.render(html_template, webpage)

    directory, html_path = get_public_path_for_page(public_path, webpage["path"])
    try:
        print(webpage["path"], directory, html_path)
        os.makedirs(directory, exist_ok=True)
        with open(html_path, 'w') as outfile:
            outfile.write(html)
    except Exception as e:
        print("Error writing output file", html_path)
        print(e)
        raise


def copytree(src, dst):
    """
    Copy a tree of files and folders
    :param src:
    :param dst:
    :param symlinks:
    :param ignore:
    :return:
    """
    names = os.listdir(src)
    if not os.path.isdir(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        except shutil.Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)


def copy_static_files(config, public_path):
    """
    Copy all static pages to output area
    :param config:
    :param public_path: Output folder
    :return:
    """

    # Copy all static files from main static area
    copytree('static', public_path)

    # Copy all theme static files
    theme = config["theme"]
    theme_static_path = os.path.join("themes", theme, "static")
    copytree(theme_static_path, public_path)


def write_site_webpages(config, html_template, public_path, webpages_list, site_structure):
    """
    Write out all pages
    :param config:
    :param html_template:
    :param public_path:
    :param webpages_list:
    :return:
    """

    try:
        shutil.rmtree(public_path, ignore_errors=False, onerror=None)
    except Exception as e:
        print("Failed to delete public area", public_path)
        print(e)

    for webpages in webpages_list:
        for webpage in webpages:
            write_webpage(config, html_template, public_path, webpage, site_structure)


def generate_site(config, html_template, public_path, webpages_list, site_structure, site_url):
    """
    Create all pages and copy all static files to public area
    :param config:
    :param html_template:
    :param public_path:
    :param webpages_list:
    :return:
    """
    write_site_webpages(config, html_template, public_path, webpages_list, site_structure)
    copy_static_files(config, public_path)
    create_site_map.create_site_map(webpages_list[0], public_path, site_url)