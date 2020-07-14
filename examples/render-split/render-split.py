from   copy    import deepcopy
import json
import os
from   pathlib import Path
from   bs4     import BeautifulSoup
import click
import jinja2

@click.command()
@click.option(
    '-o', '--out-dir',
    type    = click.Path(file_okay=False, dir_okay=True, writable=True),
    metavar = 'DIR',
    help    = 'Directory in which to place the templated files',
    default = os.curdir,
)
@click.option(
    '-i', '--intro-name',
    default      = 'intro.html',
    help         = 'Name of the templated intro file',
    show_default = True,
)
@click.option(
    '-s', '--section-fmt',
    metavar      = 'FMT',
    default      = 'section%d.html',
    help         = 'printf-format string (using "%d") for the names of the'
                   ' templated section files',
    show_default = True,
)
@click.argument('rst_json', type=click.File())
@click.argument('intro_template', type=click.Path(exists=True, dir_okay=False))
@click.argument('section_template', type=click.Path(exists=True, dir_okay=False))
def main(out_dir, intro_name, section_fmt, rst_json, intro_template,
         section_template):
    data = json.load(rst_json)
    contexts = prepare_contexts(data, intro_name, section_fmt)
    outdir = Path(out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    jenv = jinja2.Environment(
        trim_blocks   = True,
        lstrip_blocks = True,
        loader        = jinja2.FileSystemLoader(os.curdir, followlinks=True),
    )
    intro_tmpl = jenv.get_template(intro_template)
    section_tmpl = jenv.get_template(section_template)
    for i, (filename, cntxt) in enumerate(contexts):
        tmpl = section_tmpl if i else intro_tmpl
        (outdir / filename).write_text(tmpl.render(cntxt))

def prepare_contexts(data, intro_name, section_fmt):
    if data["meta"]["split_section_level"] != 1:
        raise ValueError('split_section_level of input must be 1')
    intro = data["content"].pop("intro")
    sections = data["content"].pop("sections")
    id_sections = data.pop("id_sections")
    section_filenames = [
        section_fmt % (i,) for i,_ in enumerate(sections, start=1)
    ]
    sectid2file = {
        sect["ids"][0]: fname
        for sect, fname in zip(sections, section_filenames)
    }
    href_map = {}
    for id, sectid in id_sections.items():
        if sectid == '$intro':
            href_map[f'#{id}'] = f'{intro_name}#{id}'
        else:
            href_map[f'#{id}'] = f'{sectid2file[sectid]}#{id}'
    for (sect, fname) in zip(sections, section_filenames):
        for id in sect["ids"]:
            href_map[f'#{id}'] = f'{fname}#{id}'
    intro = rewrite_hrefs(intro, href_map)
    intro_context = deepcopy(data)
    intro_context["content"]["body"] = intro
    contexts = [(intro_name, intro_context)]
    for i, (sect, fname) in enumerate(zip(sections, section_filenames)):
        sect["body"] = rewrite_hrefs(sect["body"], href_map)
        sect["this_file"] = fname
        if i+1 < len(section_filenames):
            sect["next_file"] = section_filenames[i+1]
        else:
            sect["next_file"] = None
        if i-1 >= 0:
            sect["prev_file"] = section_filenames[i-1]
        else:
            sect["prev_file"] = None
        sect["intro_file"] = intro_name
        contexts.append((fname, dict(data, section=sect)))
    return contexts

def rewrite_hrefs(htmlsrc, href_map):
    if not htmlsrc:
        return htmlsrc
    soup = BeautifulSoup(htmlsrc, 'html.parser')
    for link in soup.find_all('a', href=True):
        try:
            new_href = href_map[link["href"]]
        except KeyError:
            pass
        else:
            link["href"] = new_href
    return str(soup)

if __name__ == '__main__':
    main()
