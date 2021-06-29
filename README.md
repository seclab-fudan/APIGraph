# APIGraph
This repo hosts the source code and dataset of *APIGraph*.
For more details about our CCS 2020 paper, please see [APIGraph-website](https://xhzhang.github.io/APIGraph/).


**Update**: 
The idea of APIGraph actually not limited to Android malware detection, it can be extended to other tasks on other platforms, e.g. Windows malware detection/classification. 
As our effort to show the generality of APIGraph, we now adapt APIGraph onto Windows malware detection tasks, refer to the *windows* branch.

**Update2**:
The top30 families malware in Table 10 in the paper is uploaded, in the format of (hash,time,family).
Note the family labels were obtained using Euphony tool in 2020, which may have changed by present. 
All the malware were also downloaded from the three open repositories.

## Source Code
The source code are located in the [src](./src) directory, including: 

* **getAllEntities.py** - The script to get all entities from API documents.
* **getAllRelations.py** -  The script to extract relations between entities according to pre-defined templates.
* **TransE.py** - The script to convert each API in the relation graph into an embedding representation.
* **clusterEmbedding.py** - The script to cluster API embeddings into semantic-similar groups through k-means.
* **res** - This directory stores the resources used in above scripts, including API documents (already parsed into JSON formats), permission relation from PScout, and also some intermedia files.


## Dataset
The dataset is located in the *Dataset* directory.
This dataset contains 322,594 Android apps, including 32,089 malicious and 290,505 benign samples spanning 7 years, i.e. 2012 - 2018. 
The benign samples are all from Google Play, and downloaded from [AndroZoo](https://androzoo.uni.lu/).
The malware samples are downloaded from three sources: [VirusShare](https://virusshare.com), [VirusTotal Academic Samples](https://www.virustotal.com), and [AMD](http://amd.arguslab.org/sharing) dataset. 
The hashes are organized according to their years and maliciousness in txt format. 


**Note:**
For security and copyright reasons, we can only release the md5 hashes of these samples.
Interested users should download these samples from the above four sources. 


## Baselines

We tested four state-of-the-art Android malware classifiers as the baselines, as listed below. 
<!-- They are: MamaDroid-NDSS-2017, Drebin-NDSS-2014, Drebin-DL-Esorics-2017, and DroidEvolver-EuroSP-2019. -->

Classifiers | Publication | API feature format | Algorithms | Reproduction
---|---|---|---|---
MamaDroid | NDSS 2017 |  Markov Chain of API Calls | Random Forest | [source code](https://bitbucket.org/gianluca_students/mamadroid_code/src/master/)
DroidEvolver | Euro S&P 2019 | API Occurrence | Model Pool | [source code](https://github.com/DroidEvolver/DroidEvolver)
Drebin | NDSS 2014 | Selected API Occurrence | SVM | re-implemented
Drebin-DL | ESORICS 2017 | Selected API Occurrence | DNN | re-implemented


These four classifiers are published in top venues and their source code are publicly available or we can re-implement them, sometimes with the help of their authors.
Specially, we thank the authors of DroidEvolver for their help.  
We strictly follow their configuration to make sure our reproductions can achieve the results as stated in their paper. 



