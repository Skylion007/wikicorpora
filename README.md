WikiCorpora
===========

WikiCorpora is a tool for building corpora from Wikipedia.
WikiCorpora can download Wikipedia dump for given language,
create samples of desired size,
build vertical files with tagged terms,
perform terms inference on each article,
compile corpora
and test it by [CQL queries](https://www.sketchengine.co.uk/documentation/wiki/SkE/CorpusQuerying).

A few query examples:

* find "Achilles" followed by verb TO BE in any form

```
$ wikicorpora.py en 10 --query '"Achilles" [lemma="be"]'

#33507 outside the gates of Troy . Although the death of < Achilles is > not presented in the " Iliad " , other sources
#33562 Statius in the 1 st century AD ) state that < Achilles was > invulnerable in all of his body except for his heel
#33643 , tribe , nation . " In other words , < Achilles is > an embodiment of the grief of the people , grief
#33882 a female gladiator fighting an " Amazon " . </p><p> Birth </p> < <p> Achilles was > the son of the Nereid Thetis and Peleus , the
#34056 AD , and to no surviving previous sources , when < Achilles was > born Thetis tried to make him immortal , by dipping
#34191 the contrary , in the " Iliad " Homer mentions < Achilles being > wounded : in Book 21 the Paeonian hero Asteropaeus ,
#34706 " , the Latin summary through which the story of < Achilles was > transmitted to medieval Europe , Troilus was a young Trojan
#35442 battle with the river god Scamander who becomes angry that < Achilles is > choking his waters with all the men he has killed
#36019 guided Paris ' arrow . Some retellings also state that < Achilles was > scaling the gates of Troy and was hit with a
#36210 shoots Achilles with a divine arrow , killing him . </p> < <p> Achilles was > cremated and his ashes buried in the same urn as
```

* find words "Achilles" and "war" with at most 5 words between them

```
$ wikicorpora.py en 10 --query '"Achilles" []{0,5} "war"'

#34351 , on Mt . Pelion , to be reared . </p> < <p> Achilles in the Trojan War </p> > <p> The first two lines of the " Iliad " read
#34389 times he can not be cooled . The humanization of < Achilles by the events of the war > is an important theme of the narrative . </p><p> According to
#34905 's " Iliad " is the most famous narrative of < Achilles ' deeds in the Trojan War > . Achilles ' wrath is the central theme of the
#37845 stories </p><p> Some post-Homeric sources claim that in order to keep < Achilles safe from the war > , Thetis ( or , in some versions , Peleus
#38387 by modern scholars . The tragedies relate the deeds of < Achilles during the Trojan War > , including his defeat of Hector and eventual death when
```

* find nouns which contains "ee" and ends with "s"

```
$ wikicorpora.py en 10 --query '[word=".*ee.*s" & tag="N.*"]'

#1708 to , but to the satisfaction of his or her < needs > , whatever may be their nature . " and Pierre
#3997 – 23 saw the active participation of anarchists in varying < degrees > of protagonism . In the German uprising known as the
#4832 attempts at collectivization enactment . Factories were run through worker < committees > , agrarian areas became collectivised and run as libertarian communes
#5354 Anarchists became known for their involvement in protests against the < meetings > of the World Trade Organization ( WTO ) , Group
#9637 Light-Bearer "" . " Many of the anarchists were ardent < freethinkers > ; reprints from freethought papers such as " Lucifer ,
#11058 suffer from more intense and frequent loneliness compared to non-autistic < peers > , despite the common belief that children with autism prefer
#11280 not develop enough natural speech to meet their daily communication < needs > . Differences in communication may be present from the first
#11795 in autism proper . </p><p> Unusual eating behavior occurs in about < three-quarters > of children with ASD , to the extent that it
#12355 risk of autism appear to act during the first eight < weeks > from conception , and though this does not exclude the
#14718 the National Autism Plan for Children recommends at most 30 < weeks > from first concern to completed diagnosis and assessment , though
```

* find all terms containing "greek" anywhere in them (possibly as just a part a
  word)

```
$ wikicorpora.py en 10 --query '<term/> containing ".*greek.*"'

#21174 closely to the Hebrew or Arabic aleph . </p><p> When the < ancient Greeks > adopted the alphabet , they had no use for the
#21243 of alpha . In the earliest Greek inscriptions after the < Greek Dark Ages > , dating to the 8 th century BC , the
#21265 the letter rests upon its side , but in the < Greek alphabet > of later times it generally resembles the modern capital letter
#21308 the cross line is set . </p><p> The Etruscans brought the < Greek alphabet > to their civilization in the Italian Peninsula and left the
#33425 : </p><p> See also </p><p> References </p><p> Further reading </p><p> External links </doc></p><p><doc> Achilles </p><p> In < Greek mythology > , Achilles ( ; , " Akhilleus " , )
#33439 ( ; , " Akhilleus " , ) was a < Greek > hero of the Trojan War and the central character and
#33800 of leadership . </p><p> R. S. P. Beekes has suggested a < Pre-Greek > origin of the name . </p><p> The name Achilleus was a
#35104 refuses to fight or lead his troops alongside the other < Greek > forces . At this same time , burning with rage
#35242 <p> The Trojans , led by Hector , subsequently pushed the < Greek > army back toward the beaches and assaulted the Greek ships
#35251 the Greek army back toward the beaches and assaulted the < Greek > ships . With the Greek forces on the verge of
```

Usage
-----

```
usage: wikicorpora.py [language] [size] [TASKS]

corpus specification:
  language              2-letter code of language (ISO-639-1)
  size                  sample size specification

sampling tasks:
  --create-sample       create sample from first N articles
  --create-own-sample   create sample from selected articles

downloading tasks:
  --soft-download       download dump if not already downloaded
  --force-download      download dump (even if a dump already exists)

corpus processing tasks:
  --prevertical, -p           process dump to prevertical
  --vertical, -v              process prevertical to vertical
  --terms-inference, -t       infere all terms occurences
  --all-processing-tasks, -a  execute all corpus processing steps

compilation tasks:
  --compile, -c         create configuration file and compile corpus
  --check               print compiled corpus status generated by corpcheck
  --query QUERY         print concordances of a given CQL query

optional arguments:
  -h, --help            show help message
  --usage               show program usage
  --info                print corpus summary
```

### Some common use cases

Download dump for Czech Wikipedi, unless already dowloaded:

    $ wikicorpora.py cs --soft-download

Download dump for Czech Wikipedi, even if already dowloaded:

    $ wikicorpora.py cs --force-download

Create sample of 10 articles from downloaded English Wikipedia

    $ wikicorpora.py en 10 --create-sample

Create sample, including dump downloading if necessary

    $ wikicorpora.py en 10 --soft-download --create-sample

Create sample of selected article from Czech Wikipedia

    $ wikicorpora.py cs 3 --create-own-sample
    Title 1: Jan Hus
    Title 2: Husitské války
    Title 3: Bitva u Lipan

Create vertical from sample corpus of 10 articles from English Wikipedia,
assuming the sample was already created, but prevertical wasn't:

    $ wikicorpora.py en 10 --prevertical --vertical

Build corpus of Czech Wikipedia, including downloading and compilation

    $ wikicorpora.py cs --force-download --all-processing-tasks --compile

Build corpus of Czech Wikipedia, but without downloading and compilation

    $ wikicorpora.py cs --processing-tasks

Create prevertical from Slovak Wikipedia, including downloading if necessary

    $ wikicorpora.py sk --soft-download --prevertical

Create vertical from prevertical of Slovak Wikipedia

    $ wikicorpora.py sk --vertical

Perform terms inference on vertical of Slovak Wikipedia

    $ wikicorpora.py sk --terms-inference

Compile vertical of English Wikipedia

    $ wikicorpora.py en --compile

Run corpus check and print results:

    $ wikicorpora.py en --check

Searching in corpus of English Wikipedia:

    $ wikicorpora.py en --query='<CQL expression>'

Print corpus summary:

    $ wikicorpora.py en 10 [--info]

Print summary of all Wikipedia corpora:

    $ wikicorpora.py --info

Print help:

    $ wikicorpora.py --help


Installation and configuration
------------------------------

It's supposed to be run on Alba server in Natural Language Processing Centre
at the Faculty of Informatics, Masaryk University, Brno. Some portions of
the code can be run anywhere, but for full functionality WikiCorpora depends
on several NLP tools, such as unitok, desamb, treetagger and compilecorp.

To install WikiCorpora, just clone this repository anywhere and
create local environment configuration file with name `environment-config.yaml`
in project root directory. Content of the configuration file is following:

```
paths:
    verticals:          '<path to directory for all verticals>'
    registry:           '<path to directory for registry files'
    compiled-corpora:   '<path to directory for compiled corpora>'
tools:
    unitok:             '<path to unitok>'
    sentence-tagger:    '<path to sentence-tagger script>'
    desamb:             '<path to desamb>'
    treetagger:         '<path to treetagger scripts (using substituable {lang})>'
    treetagger-en:      '<path to special treetagger script for english>'
```

As a fallback, `environment-config-default.yaml` is used.
