# pdfstat

Track progress of reading a ebook/document over time. Works only with [zathura](https://pwmt.org/projects/zathura/) (for now).

Also contains `open-pdf`, a zathura launcher using [rofi](https://github.com/davatorium/rofi).

## Usage

First add some documents you want to track.

```bash
pdfstat track 'Structure and Interpretation of Computer Programs.pdf'
pdfstat track '~/pdfs/Programming/What Every Programmer Should Know About Memory.pdf'
```

Then, run `pdfstat update` from time to time. You can set up a systemd user timer to run it automatically. You can also use a launcher like `open-pdf` from this repo that will automatically update the database when you close zathura.

After a few days, you can query for some stats.

```console
$ pdfstat show
Structure and Interpretation of Class.. : 45/567 (8%)
What Every Programmer Should Know Abo.. : 20/114 (18%)
The Art of Electronics.pdf: 110/1225 (9%) - 1.44 pages/day, 775 days left
```

### plotpdf

You can also make a plot with the `plotpdf` script:
``` bash
plotpdf ~/pdfs/Electronics/The\ Art\ of\ Electronics.pdf abc.png --goal 1 --days 60
```

![Image](https://i.imgur.com/DGpQIrE.png)

### open-pdf

`openpdf` is a simple way to open a document in zathura. It lists all documents in a directory, sorts them by last time opened, and applies some formating to the names. Once a document is chosen it opens it in zathura. When zathura is closed, it updates the pdfstat database.