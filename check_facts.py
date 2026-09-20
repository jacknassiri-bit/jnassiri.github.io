import re, subprocess, collections, sys


files = subprocess.check_output(["git", "diff", "--name-only", "main"], text=True).split()


def text(s):


    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)


    s = re.sub(r"<[^>]+>", " ", s)


    return s.replace("&nbsp;", " ")


bad = False


for f in files:


    if not f.endswith(".html"):


        continue


    old = subprocess.check_output(["git", "show", f"main:{f}"], text=True)


    new = open(f, encoding="utf-8").read()


    for label, pat in [("number", r"\d[\d,.]*%?"), ("citation", r"\([A-Z][A-Za-z\-\. ]+(?:et al\.|and [A-Z][a-z]+)\)"), ("href", r'href="[^"]+"')]:


        src_old = old if label == "href" else text(old)


        src_new = new if label == "href" else text(new)


        a = collections.Counter(re.findall(pat, src_old))


        b = collections.Counter(re.findall(pat, src_new))


        lost = a - b


        if lost and label != "number":


            print(f"{f}: {label} lost -> {dict(lost)}"); bad = True


        elif lost and label == "number":


            print(f"{f}: numbers no longer present -> {dict(lost)}  (only OK if a sentence with that number was cut on purpose)")


sys.exit(1 if bad else 0)
