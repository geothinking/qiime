#!/usr/bin/env python

from os.path import join, exists
from os import remove
from re import search
from cogent.util.unit_test import TestCase, main
from cogent.app.util import get_tmp_filename
from qiime.pycogent_backports.blat import Blat, assign_reads_to_database, \
                assign_dna_reads_to_dna_database, \
                assign_dna_reads_to_protein_database

__author__ = "Adam Robbins-Pianka"
__copyright__ = "Copyright 2007-2012, The QIIME Project"
__credits__ = ["Adam Robbins-Pianka", "Daniel McDonald"]
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Adam Robbins-Pianka"
__email__ = "adam.robbinspianka@colorado.edu"
__status__ = "Prototype"

class BlatTests(TestCase):
    files_to_remove = []

    def setUp(self):
        """Sets up files for testing.
        """
        self.test_db_prot_filename = get_tmp_filename().replace('"', '')
        self.test_db_prot = open(self.test_db_prot_filename, 'w')
        self.test_db_dna_filename = get_tmp_filename().replace('"', '')
        self.test_db_dna = open(self.test_db_dna_filename, 'w')
        self.test_query_filename = get_tmp_filename().replace('"', '')
        self.test_query = open(self.test_query_filename, 'w')

        # write the global variables at the bottom of this file to the
        # temporary test files. Can't use file-like objects because the
        # external application needs actual files.
        self.test_db_prot.write('\n'.join(test_db_prot))
        self.test_db_dna.write('\n'.join(test_db_dna))
        self.test_query.write('\n'.join(test_query))

        # close the files
        self.test_db_prot.close()
        self.test_db_dna.close()
        self.test_query.close()

        # prepare output file path
        self.testout = get_tmp_filename().replace('"', '')

        self.files_to_remove += [self.test_db_prot_filename,
                            self.test_db_dna_filename,
                            self.test_query_filename, self.testout]

    def tearDown(self):
        """Removes temporary files created during the tests
        """
        for filename in self.files_to_remove:
            if exists(filename): remove(filename)

    def test_assign_reads_to_database(self):
        """Tests that assign_reads_to_database works as expected.

        Checks the output file against the expected result when known
        database and query files are used.
        """
        exp = [l for l in assign_reads_exp if not l.startswith('#')]
        obs_lines = assign_reads_to_database(self.test_query_filename,
                                             self.test_db_dna_filename,
                                             self.testout).read().splitlines()
        obs = [l for l in obs_lines if not l.startswith('#')]
        
        self.assertEqual(obs, exp)

    def test_assign_dna_reads_to_dna_database(self):
        """Tests that assign_dna_reads_to_dna_database works as expected.

        Checks the output file against the expected result when known
        database and query files are used.
        """
        exp = [l for l in assign_reads_exp if not l.startswith('#')]

        obs_lines = assign_dna_reads_to_dna_database(self.test_query_filename,
                                             self.test_db_dna_filename,
                                             self.testout).read().splitlines()
        obs = [l for l in obs_lines if not l.startswith('#')]
        
        self.assertEqual(obs, exp)

    def test_assign_dna_reads_to_protein_database(self):
        """Tests that assign_dna_reads_to_protein_database works as expected.

        Checks the output file against the expected result when known
        database and query files are used.
        """
        exp = [l for l in assign_reads_prot_exp if not l.startswith('#')]

        obs_lines = assign_dna_reads_to_protein_database(
                    self.test_query_filename,
                    self.test_db_prot_filename,
                    self.testout).read().splitlines()
        obs = [l for l in obs_lines if not l.startswith('#')]
        
        self.assertEqual(obs, exp)

    def test_get_base_command(self):
        """Tests that _get_base_command generates the proper command given
        various inputs.
        """
        test_parameters_blank = {}
        files = (self.test_query_filename, self.test_db_dna_filename, 
                self.testout)
        exp_blank = 'blat %s %s %s' % (files[1], files[0], files[2])

        # initialize a Blat instance with these parameters and get the
        # command string
        b = Blat(params = {}, HALT_EXEC=True)
        # need to set the positional parameters' values
        b._input_as_list(files)
        cmd = b._get_base_command()

        # find the end of the cd command and trim the base command
        cmd_index = search('cd ".+"; ', cmd).end()
        cmd = cmd[cmd_index:]
        self.assertEqual(cmd, exp_blank)

        test_parameters_1 = {
            '-t': 'dna',
            '-q': 'dna',
            '-ooc': '11.ooc',
            '-tileSize': 1,
            '-stepSize': 2,
            '-oneOff': 1,
            '-minMatch': 2,
            '-minScore': 3,
            '-minIdentity': 4,
            '-maxGap': 5,
            '-makeOoc': 'N.ooc',
            '-repMatch': 6,
            '-mask': 'lower',
            '-qMask': 'lower',
            '-repeats': 'lower',
            '-minRepDivergence': 7,
            '-dots': 8,
            '-out': 'psl',
            '-maxIntron': 9}
        exp_1 = 'blat %s %s ' % (files[1], files[0]) + \
                '-dots=8 -makeOoc="N.ooc" -mask=lower -maxGap=5 ' + \
                '-maxIntron=9 -minIdentity=4 -minMatch=2 ' + \
                '-minRepDivergence=7 -minScore=3 -oneOff=1 -ooc="11.ooc" ' + \
                '-out=psl -q=dna -qMask=lower -repMatch=6 -repeats=lower ' + \
                '-stepSize=2 -t=dna -tileSize=1 %s' % files[2]

        # initialize a Blat instance with these parameters and get the
        # command string
        b = Blat(params = test_parameters_1, HALT_EXEC=True)
        # need to set the positional parameters' values
        b._input_as_list(files)
        cmd = b._get_base_command()

        # find the end of the cd command and trim the base command
        cmd_index = search('cd ".+"; ', cmd).end()
        cmd = cmd[cmd_index:]
        self.assertEqual(cmd, exp_1)

        test_parameters_2 = {
            '-tileSize': 1,
            '-stepSize': 2,
            '-minMatch': 2,
            '-minScore': 3,
            '-minIdentity': 4,
            '-maxGap': 5,
            '-makeOoc': 'N.ooc',
            '-out': 'psl',
            '-maxIntron': 9}
        exp_2 = 'blat %s %s ' % (files[1], files[0]) + \
                '-makeOoc="N.ooc" -maxGap=5 -maxIntron=9 -minIdentity=4 ' + \
                '-minMatch=2 -minScore=3 -out=psl -stepSize=2 ' + \
                '-tileSize=1 %s' % files[2]

        # initialize a Blat instance with these parameters and get the
        # command string
        b = Blat(params = test_parameters_2, HALT_EXEC=True)
        # need to set the positional parameters' values
        b._input_as_list(files)
        cmd = b._get_base_command()

        # find the end of the cd command and trim the base command
        cmd_index = search('cd ".+"; ', cmd).end()
        cmd = cmd[cmd_index:]
        self.assertEqual(cmd, exp_2)

assign_reads_exp = """# BLAT 34 [2006/03/10]
# Query: NZ_GG770509_647533119
# Database: test_db.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG770509_647533119	NZ_GG770509_647533119	100.00	1371	0	0	1	1371	1	1371	0.0e+00	2187.0
NZ_GG770509_647533119	NZ_ACIZ01000148_643886127	85.49	634	92	0	336	969	337	970	4.5e-234	807.0
NZ_GG770509_647533119	NZ_ACIZ01000148_643886127	86.08	237	33	0	1135	1371	1137	1373	1.2e-77	287.0
NZ_GG770509_647533119	NZ_ACIZ01000148_643886127	83.12	154	26	0	976	1129	977	1130	2.2e-48	190.0
NZ_GG770509_647533119	NZ_GG739926_647533195	78.42	329	71	0	656	984	657	985	4.8e-97	351.0
NZ_GG770509_647533119	NZ_GG739926_647533195	89.09	110	11	1	1138	1246	1141	1250	1.1e-30	131.0
NZ_GG770509_647533119	NZ_GG739926_647533195	86.96	69	9	0	1021	1089	1023	1091	3.2e-20	96.0
NZ_GG770509_647533119	NZ_GG739926_647533195	75.26	97	22	2	356	450	356	452	2.3e-13	73.0
NZ_GG770509_647533119	NZ_GG739926_647533195	90.57	53	5	0	1319	1371	1315	1367	2.5e-10	63.0
NZ_GG770509_647533119	NZ_GG739926_647533195	81.82	22	4	0	989	1010	992	1013	1.5e+02	24.0
# BLAT 34 [2006/03/10]
# Query: NZ_GG739926_647533195
# Database: test_db.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG739926_647533195	NZ_GG739926_647533195	100.00	1367	0	0	1	1367	1	1367	0.0e+00	2235.0
NZ_GG739926_647533195	NZ_ACIZ01000148_643886127	76.22	572	136	0	414	985	414	985	1.7e-158	556.0
NZ_GG739926_647533195	NZ_ACIZ01000148_643886127	76.80	181	42	0	1023	1203	1022	1202	6.4e-53	205.0
NZ_GG739926_647533195	NZ_ACIZ01000148_643886127	96.00	50	2	0	1209	1258	1207	1256	6.4e-14	75.0
NZ_GG739926_647533195	NZ_ACIZ01000148_643886127	88.68	53	6	0	1315	1367	1321	1373	1.6e-09	61.0
NZ_GG739926_647533195	NZ_ACIZ01000148_643886127	77.27	22	5	0	992	1013	990	1011	8.5e+02	22.0
NZ_GG739926_647533195	NZ_GG770509_647533119	79.29	280	58	0	657	936	656	935	9.9e-82	301.0
NZ_GG739926_647533195	NZ_GG770509_647533119	89.09	110	11	1	1141	1250	1138	1246	1.1e-30	131.0
NZ_GG739926_647533195	NZ_GG770509_647533119	86.96	69	9	0	1023	1091	1021	1089	3.2e-20	96.0
NZ_GG739926_647533195	NZ_GG770509_647533119	75.26	97	22	2	356	452	356	450	2.3e-13	73.0
NZ_GG739926_647533195	NZ_GG770509_647533119	90.57	53	5	0	1315	1367	1319	1371	2.5e-10	63.0
NZ_GG739926_647533195	NZ_GG770509_647533119	80.00	30	6	0	956	985	955	984	1.2e-03	41.0
NZ_GG739926_647533195	NZ_GG770509_647533119	81.82	22	4	0	992	1013	989	1010	1.5e+02	24.0
# BLAT 34 [2006/03/10]
# Query: NZ_ACIZ01000148_643886127
# Database: test_db.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_ACIZ01000148_643886127	NZ_ACIZ01000148_643886127	100.00	1373	0	0	1	1373	1	1373	0.0e+00	2165.0
NZ_ACIZ01000148_643886127	NZ_GG770509_647533119	85.49	634	92	0	337	970	336	969	4.5e-234	807.0
NZ_ACIZ01000148_643886127	NZ_GG770509_647533119	86.08	237	33	0	1137	1373	1135	1371	1.2e-77	287.0
NZ_ACIZ01000148_643886127	NZ_GG770509_647533119	83.12	154	26	0	977	1130	976	1129	2.2e-48	190.0
NZ_ACIZ01000148_643886127	NZ_GG739926_647533195	76.22	572	136	0	414	985	414	985	1.7e-158	556.0
NZ_ACIZ01000148_643886127	NZ_GG739926_647533195	76.80	181	42	0	1022	1202	1023	1203	6.4e-53	205.0
NZ_ACIZ01000148_643886127	NZ_GG739926_647533195	96.00	50	2	0	1207	1256	1209	1258	6.4e-14	75.0
NZ_ACIZ01000148_643886127	NZ_GG739926_647533195	88.68	53	6	0	1321	1373	1315	1367	1.6e-09	61.0
NZ_ACIZ01000148_643886127	NZ_GG739926_647533195	77.27	22	5	0	990	1011	992	1013	8.5e+02	22.0
""".splitlines()

assign_reads_prot_exp = """# BLAT 34x13 [2009/02/26]
# Query: NZ_GG770509_647533119_frame_1
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG770509_647533119_frame_1	NZ_GG770509_647533119	96.83	441	0	7	1	427	1	441	8.9e-254	872.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_GG770509_647533119_frame_2
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG770509_647533119_frame_2	NZ_ACIZ01000148_643886127	85.37	41	6	0	359	399	362	402	8.0e-13	72.0
NZ_GG770509_647533119_frame_2	NZ_ACIZ01000148_643886127	93.75	16	1	0	419	434	421	436	1.3e+00	31.0
NZ_GG770509_647533119_frame_2	NZ_GG739926_647533195	75.86	29	7	0	320	348	326	354	2.9e-04	43.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_GG770509_647533119_frame_3
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG770509_647533119_frame_3	NZ_ACIZ01000148_643886127	80.61	98	19	0	210	307	209	306	7.5e-39	158.0
NZ_GG770509_647533119_frame_3	NZ_ACIZ01000148_643886127	66.33	98	33	0	43	140	44	141	8.9e-27	118.0
NZ_GG770509_647533119_frame_3	NZ_ACIZ01000148_643886127	78.95	38	8	0	310	347	308	345	2.3e-08	57.0
NZ_GG770509_647533119_frame_3	NZ_ACIZ01000148_643886127	66.67	30	10	0	178	207	178	207	2.5e-01	33.0
NZ_GG770509_647533119_frame_3	NZ_GG739926_647533195	53.00	100	47	0	131	230	134	233	1.9e-18	90.0
NZ_GG770509_647533119_frame_3	NZ_GG739926_647533195	68.89	45	14	0	238	282	241	285	5.9e-09	59.0
NZ_GG770509_647533119_frame_3	NZ_GG739926_647533195	72.09	43	12	0	63	105	66	108	3.0e-08	56.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_GG739926_647533195_frame_1
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG739926_647533195_frame_1	NZ_GG739926_647533195	100.00	437	0	0	1	437	1	437	1.7e-263	904.0
NZ_GG739926_647533195_frame_1	NZ_ACIZ01000148_643886127	69.86	73	22	0	213	285	209	281	1.1e-20	98.0
NZ_GG739926_647533195_frame_1	NZ_ACIZ01000148_643886127	53.33	60	28	0	148	207	145	204	1.3e-06	51.0
NZ_GG739926_647533195_frame_1	NZ_ACIZ01000148_643886127	60.53	38	15	0	66	103	64	101	1.9e-03	41.0
NZ_GG739926_647533195_frame_1	NZ_ACIZ01000148_643886127	76.92	26	6	0	2	27	3	28	9.7e-03	38.0
NZ_GG739926_647533195_frame_1	NZ_ACIZ01000148_643886127	69.57	23	7	0	288	310	285	307	4.8e+00	29.0
NZ_GG739926_647533195_frame_1	NZ_ACIZ01000148_643886127	90.00	10	1	0	134	143	132	141	1.6e+04	18.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_GG739926_647533195_frame_2
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG739926_647533195_frame_2	NZ_GG770509_647533119	66.67	42	14	0	270	311	276	317	2.3e-08	57.0
NZ_GG739926_647533195_frame_2	NZ_GG770509_647533119	60.00	45	18	0	185	229	188	232	3.9e-06	49.0
NZ_GG739926_647533195_frame_2	NZ_GG770509_647533119	80.00	20	4	0	247	266	251	270	5.6e-01	32.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_GG739926_647533195_frame_3
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_GG739926_647533195_frame_3	NZ_ACIZ01000148_643886127	94.44	18	1	0	390	407	385	402	4.3e-03	39.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_ACIZ01000148_643886127_frame_1
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_ACIZ01000148_643886127_frame_1	NZ_ACIZ01000148_643886127	100.00	436	0	0	1	436	1	436	2.1e-261	897.0
NZ_ACIZ01000148_643886127_frame_1	NZ_GG739926_647533195	78.57	42	9	0	240	281	244	285	4.0e-10	63.0
NZ_ACIZ01000148_643886127_frame_1	NZ_GG739926_647533195	60.53	38	15	0	64	101	66	103	1.9e-03	41.0
NZ_ACIZ01000148_643886127_frame_1	NZ_GG739926_647533195	76.92	26	6	0	3	28	2	27	9.7e-03	38.0
NZ_ACIZ01000148_643886127_frame_1	NZ_GG739926_647533195	69.57	23	7	0	285	307	288	310	4.8e+00	29.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_ACIZ01000148_643886127_frame_2
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_ACIZ01000148_643886127_frame_2	NZ_GG770509_647533119	79.59	147	26	2	182	324	189	335	2.3e-61	233.0
NZ_ACIZ01000148_643886127_frame_2	NZ_GG770509_647533119	72.73	33	9	0	128	160	137	169	5.0e-04	42.0
NZ_ACIZ01000148_643886127_frame_2	NZ_GG770509_647533119	90.91	22	2	0	70	91	76	97	2.5e-03	40.0
# BLAT 34x13 [2009/02/26]
# Query: NZ_ACIZ01000148_643886127_frame_3
# Database: /home/adro2179/metagenome/test_db_prot.fasta
# Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score
NZ_ACIZ01000148_643886127_frame_3	NZ_GG770509_647533119	84.21	38	4	1	360	395	367	404	3.0e-08	56.0
NZ_ACIZ01000148_643886127_frame_3	NZ_GG770509_647533119	94.12	17	1	0	413	429	425	441	1.6e+00	31.0
NZ_ACIZ01000148_643886127_frame_3	NZ_GG739926_647533195	78.57	28	5	1	321	347	326	353	1.5e-03	41.0"""
assign_reads_prot_exp = assign_reads_prot_exp.splitlines()

test_db_prot = """>NZ_GG770509_647533119
YLEFDPGSERTLAAGLTHASRASGRRVSNAWERTICYGITQGNLCYRMetWKVGKSARVGLASWWGKGSPRRRSIAGLRGSATLGLRHGPDSYGRQQWGILDNGRKPDPAMetPRERPGCKALSPVKMetTVTGEEAPANFVPAAAVIRRGLALFGFTGRKAHVGGLLSQGNPGAQPRNCLYWKSVWRVEFRVRNSIFGGTPVAKAAHWTNRGAKAWGANRIRYPGSPRRKRMetLAVGASVAQLTHTFRLGSAVARLKLKGIDGGPHKRWSMetWFNSKQRAEPYQPLTSTGAAWLSSARVVRCWVKSRNERNPRPLPAWALGDCRAGGRWGRQVLMetALTGWATHVLQWWSVGSEHASVSSPPSQFGCTLQLECRSWNRSRISMetPRIRSRALYTPPVTPWELVLPEGACAGDHGRVSDWGEVVTRPGNLRLDHLLS
>NZ_GG739926_647533195
WEFDPGSGTLATGLTHASRGTGARVSNAYPTFPRPRDNLPKGRLIPYVQSRSRMGMRPISLLAGQRPTKASIGRGSERKAPHTGTETRSRLLREAAVRNIGQWAEATSQVACRTTAYGLTAFMRGYAGTAIRTGFRASSRGNTEGPGVIRIYWVRERRPPCKRAVKSSGPTAALRRELLGLSAPEAGGIRGVAVKCLDITKNPDCEGSPLWRLTLRLEGAGIEQDIPWSARTMDTRCPALGGQAKALSIPPGEYAGNGETQRNRGPAQAEEHVVFDDTRGTLPGLELRCCMVVVSSCREVSAQVPRAQPLSAVAIGRALCGHCRRKVEEGGDDVKSARPLRPGPHTCYNGRQRAVRAQVRVNPLRSQFGWGLQPDPRSWIRSRISHGAVNTFPGLVHTARQAMKAGGASPCRPRAKPVIGAKSQGSRTGRCGWNTSF
>NZ_ACIZ01000148_643886127
NMEFDPGSGTLAACLIHASRTSGGRVSNTWVTCPVGDNIWKQMLIPHKESRFWMDPRRISLVRRLTKAMIRSRTERLIGHIGTETRPKLLREAAVGNLPQWTQVWSNAAVKKAFGSNSVVGEDDGIQPESHGLRASSRGNTVASVIRIYWASERRRFFKSDVKALGLTEEVHRKLGNLSAEEDSGTPCVAVKCVDIWKNTSGEGGCLVLTLRLESMGSEQDIPWSMPTMNARCWSFSAAANALSIPPGEYDRKVETQRNRGPAQAVEHVVFEATRRTLPGLDIDRWCMVVVSSCREMLGVPQRAQPLLVASMGTLVRLPVTNRRKVGMTSNHHAPYDLGYTRATMDGNELRDREVKLISSILSSDVGCNSPTEVGIASNRGSARRGEYVPGPCTHRPSHHESLHPKPVRSEPSKVGQMIRVKSQGSRRRTCGWITS"""
test_db_prot = test_db_prot.splitlines()

test_db_dna = """>NZ_GG770509_647533119
UACUUGGAGUUUGAUCCUGGCUCAGAACGAACGCUGGCGGCAGGCUUAACACAUGCAAGUCGAGCGAGCGGCAGACGGGUGAGUAACGCGUGGGAACGUACCAUUUGCUACGGAAUAACUCAGGGAAACUUGUGCUAAUACCGUAUGUGGAAAGUCGGCAAAUGAUCGGCCCGCGUUGGAUUAGCUAGUUGGUGGGGUAAAGGCUCACCAAGGCGACGAUCCAUAGCUGGUCUGAGAGGAUGAUCAGCCACACUGGGACUGAGACACGGCCCAGACUCCUACGGGAGGCAGCAGUGGGGAAUAUUGGACAAUGGGCGCAAGCCUGAUCCAGCCAUGCCGCGUGAGUGAUGAAGGCCCUAGGGUUGUAAAGCUCUUUCACCGGUGAAGAUGACGGUAACCGGAGAAGAAGCCCCGGCUAACUUCGUGCCAGCAGCCGCGGUAAUACGAAGGGGGCUAGCGUUGUUCGGAUUUACUGGGCGUAAAGCGCACGUAGGCGGACUUUUAAGUCAGGGGUGAAAUCCCGGGGCUCAACCCCGGAACUGCCUUUGAUACUGGAAGUCUUGAGUAUGGUAGAGGUGAGUGGAAUUCCGAGUGUAGAGGUGAAAUUCGUAGAUAUUCGGAGGAACACCAGUGGCGAAGGCGGCUCACUGGACCAACUGACGCUGAGGUGCGAAAGCGUGGGGAGCAAACAGGAUUAGAUACCCUGGUAGUCCACGCCGUAAACGAUGAAUGUUAGCCGUCGGGGCUUCGGUGGCGCAGCUAACGCAUUAAACAUUCCGCCUGGGGAGUGCGGUCGCAAGAUUAAAACUCAAAGGAAUUGACGGGGGCCCGCACAAGCGGUGGAGCAUGUGGUUUAAUUCGAAGCAACGCGCAGAACCUUACCAGCCCUUGACAUCGACAGGUGCUGCAUGGCUGUCGUCAGCUCGUGUCGUGAGAUGUUGGGUUAAGUCCCGCAACGAGCGCAACCCUCGCCCUUAGUUGCCAGCAUGGGCACUCUAAGGGGACUGCCGGUGAUAAGCCGGAGGAAGGUGGGGAUGACGUCAAGUCCUCAUGGCCCUUACGGGCUGGGCUACACACGUGCUACAAUGGUGGUCAGUGGGCAGCGAGCACGCGAGUGUGAGCUAAUCUCCGCCAUCUCAGUUCGGAUGCACUCUGCAACUCGAGUGCAGAAGUUGGAAUCGCUAGUAAUCGCGGAUCAGCAUGCCGCGGUGAAUACGUUCCCGGGCCUUGUACACACCGCCCGUCACACCAUGGGAGUUGGUUUUACCCGAAGGCGCUUGCUAGGCAGGCGACCACGGUAGGGUCAGCGACUGGGGUGAAGUCGUAACAAGGUAGCCGUAGGGGAACCUGCGGCUGGAUCACCUCCUUUCU
>NZ_GG739926_647533195
UAAUGGGAGUUUGAUCCUGGCUCAGGAUGAACGCUGGCUACAGGCUUAACACAUGCAAGUCGAGGGACCGGCGCACGGGUGAGUAACGCGUAUCCAACCUUCCCGCGACCAAGGGAUAACCUGCCGAAAGGCAGACUAAUACCUUAUGUCCAAAGUCGGUCACGGAUGGGGAUGCGUCCGAUUAGCUUGUUGGCGGGGCAACGGCCCACCAAGGCAUCGAUCGGUAGGGGUUCUGAGAGGAAGGCCCCCCACACUGGAACUGAGACACGGUCCAGACUCCUACGGGAGGCAGCAGUGAGGAAUAUUGGUCAAUGGGCGGAAGCCUGAACCAGCCAAGUAGCGUGCAGGACGACGGCCUACGGGUUGUAAACUGCUUUUAUGCGGGGAUAUGCAGGUACCGCAUGAAUAAGGACCGGCUAAUUCCGUGCCAGCAGCCGCGGUAAUACGGAAGGUCCGGGCGUUAUCCGGAUUUAUUGGGUUUAAAGGGAGCGCAGGCCGCCGUGCAAGCGUGCCGUGAAAAGCAGCGGCCCAACCGCUGCCCUGCGGCGCGAACUGCUUGGCUUGAGUGCGCCGGAAGCGGGCGGAAUUCGUGGUGUAGCGGUGAAAUGCUUAGAUAUCACGAAGAACCCCGAUUGCGAAGGCAGCCCGCUGUGGCGACUGACGCUGAGGCUCGAAGGUGCGGGUAUCGAACAGGAUUAGAUACCCUGGUAGUCCGCACGGUAAACGAUGGAUACCCGCUGUCCGGCUCUGGGCGGCCAAGCGAAAGCGUUAAGUAUCCCACCUGGGGAGUACGCCGGCAACGGUGAAACUCAAAGGAAUUGACGGGGGCCCGCACAAGCGGAGGAACAUGUGGUUUAAUUCGAUGAUACGCGAGGAACCUUACCCGGGCUUGAAUUGUGAAGGUGCUGCAUGGUUGUCGUCAGCUCGUGCCGUGAGGUGUCGGCUCAAGUGCCAUAACGAGCGCAACCCCUCUCCGCAGUUGCCAUCGGCCGGGCACUCUGCGGACACUGCCGCCGCAAGGUGGAGGAAGGUGGGGAUGACGUCAAAUCAGCACGGCCCUUACGUCCGGGGCCACACACGUGUUACAAUGGCCGGCAGAGGGCUGUCCGCGCGCAAGUGCGGGUGAAUCCCCUCCGGUCCCAGUUCGGAUGGGGUCUGCAACCCGACCCCAGAAGCUGGAUUCGCUAGUAAUCGCGCAUCAGCCAUGGCGCGGUGAAUACGUUCCCGGGCCUUGUACACACCGCCCGUCAAGCCAUGAAAGCCGGGGGUGCCUGAAGUCCGUGUCGGCCUAGGGCAAAACCGGUGAUUGGGGCUAAGUCGUAACAAGGUAGCCGUACCGGAAGGUGCGGCUGGAACACCUCCUUUCU
>NZ_ACIZ01000148_643886127
AAUAUGGAGUUUGAUCCUGGCUCAGGAUGAACGCUGGCGGCGUGCCUAAUACAUGCAAGUCGAACGAGUGGCGGACGGGUGAGUAACACGUGGGUAACCUGCCCUUAAGUGGGGGAUAACAUUUGGAAACAGAUGCUAAUACCGCAUAAAGAAAGUCGCUUUUGGAUGGACCCGCGGCGUAUUAGCUAGUUGGUGAGGUAACGGCUCACCAAGGCAAUGAUACGUAGCCGAACUGAGAGGUUGAUCGGCCACAUUGGGACUGAGACACGGCCCAAACUCCUACGGGAGGCAGCAGUAGGGAAUCUUCCACAAUGGACGCAAGUCUGAUGGAGCAACGCCGCGUGAGUGAAGAAGGCUUUCGGGUCGUAAAACUCUGUUGUUGGAGAAGAUGACGGUAUCCAACCAGAAAGCCACGGCUAACUACGUGCCAGCAGCCGCGGUAAUACGUAGGUGGCAAGCGUUAUCCGGAUUUAUUGGGCGUAAAGCGAGCGCAGGCGGUUUUUUAAGUCUGAUGUGAAAGCCCUCGGCUUAACCGAGGAAGUGCAUCGGAAACUGGGAAACUUGAGUGCAGAAGAGGACAGUGGAACUCCAUGUGUAGCGGUGAAAUGCGUAGAUAUAUGGAAGAACACCAGUGGCGAAGGCGGCUGUCUGGUCUGACUGACGCUGAGGCUCGAAAGCAUGGGUAGCGAACAGGAUUAGAUACCCUGGUAGUCCAUGCCGUAAACGAUGAAUGCUAGGUGUUGGAGCUUCAGUGCCGCAGCUAACGCAUUAAGCAUUCCGCCUGGGGAGUACGACCGCAAGGUUGAAACUCAAAGGAAUUGACGGGGGCCCGCACAAGCGGUGGAGCAUGUGGUUUAAUUCGAAGCAACGCGAAGAACCUUACCAGGUCUUGACAUCGACAGGUGGUGCAUGGUUGUCGUCAGCUCGUGUCGUGAGAUGUUGGGUUAAGUCCCGCAACGAGCGCAACCCUUAUGACUAGUUGCCAGCAUGGGCACUCUAGUAAGACUGCCGGUGACAAACCGGAGGAAGGUGGGGAUGACGUCAAAUCAUCAUGCCCCUUAUGACCUGGGCUACACACGUGCUACAAUGGAUGGCAACGAGUUGCGAGACCGCGAGGUCAAGCUAAUCUCUUCCAUUCUCAGUUCGGAUGUAGGCUGCAACUCGCCUACAGAAGUCGGAAUCGCUAGUAAUCGCGGAUCAGCACGCCGCGGUGAAUACGUUCCCGGGCCUUGUACACACCGCCCGUCACACCAUGAGAGUUUGUAACACCCGAAGCCGGUGCGUAGCGAGCCGUCUAAGGUGGGACAAAUGAUUAGGGUGAAGUCGUAACAAGGUAGCCGUAGGAGAACCUGCGGCUGGAUCACCUCCUUUCU"""
test_db_dna = test_db_dna.splitlines()

test_query = """>NZ_GG770509_647533119
UACUUGGAGUUUGAUCCUGGCUCAGAACGAACGCUGGCGGCAGGCUUAACACAUGCAAGUCGAGCGAGCGGCAGACGGGUGAGUAACGCGUGGGAACGUACCAUUUGCUACGGAAUAACUCAGGGAAACUUGUGCUAAUACCGUAUGUGGAAAGUCGGCAAAUGAUCGGCCCGCGUUGGAUUAGCUAGUUGGUGGGGUAAAGGCUCACCAAGGCGACGAUCCAUAGCUGGUCUGAGAGGAUGAUCAGCCACACUGGGACUGAGACACGGCCCAGACUCCUACGGGAGGCAGCAGUGGGGAAUAUUGGACAAUGGGCGCAAGCCUGAUCCAGCCAUGCCGCGUGAGUGAUGAAGGCCCUAGGGUUGUAAAGCUCUUUCACCGGUGAAGAUGACGGUAACCGGAGAAGAAGCCCCGGCUAACUUCGUGCCAGCAGCCGCGGUAAUACGAAGGGGGCUAGCGUUGUUCGGAUUUACUGGGCGUAAAGCGCACGUAGGCGGACUUUUAAGUCAGGGGUGAAAUCCCGGGGCUCAACCCCGGAACUGCCUUUGAUACUGGAAGUCUUGAGUAUGGUAGAGGUGAGUGGAAUUCCGAGUGUAGAGGUGAAAUUCGUAGAUAUUCGGAGGAACACCAGUGGCGAAGGCGGCUCACUGGACCAACUGACGCUGAGGUGCGAAAGCGUGGGGAGCAAACAGGAUUAGAUACCCUGGUAGUCCACGCCGUAAACGAUGAAUGUUAGCCGUCGGGGCUUCGGUGGCGCAGCUAACGCAUUAAACAUUCCGCCUGGGGAGUGCGGUCGCAAGAUUAAAACUCAAAGGAAUUGACGGGGGCCCGCACAAGCGGUGGAGCAUGUGGUUUAAUUCGAAGCAACGCGCAGAACCUUACCAGCCCUUGACAUCGACAGGUGCUGCAUGGCUGUCGUCAGCUCGUGUCGUGAGAUGUUGGGUUAAGUCCCGCAACGAGCGCAACCCUCGCCCUUAGUUGCCAGCAUGGGCACUCUAAGGGGACUGCCGGUGAUAAGCCGGAGGAAGGUGGGGAUGACGUCAAGUCCUCAUGGCCCUUACGGGCUGGGCUACACACGUGCUACAAUGGUGGUCAGUGGGCAGCGAGCACGCGAGUGUGAGCUAAUCUCCGCCAUCUCAGUUCGGAUGCACUCUGCAACUCGAGUGCAGAAGUUGGAAUCGCUAGUAAUCGCGGAUCAGCAUGCCGCGGUGAAUACGUUCCCGGGCCUUGUACACACCGCCCGUCACACCAUGGGAGUUGGUUUUACCCGAAGGCGCUUGCUAGGCAGGCGACCACGGUAGGGUCAGCGACUGGGGUGAAGUCGUAACAAGGUAGCCGUAGGGGAACCUGCGGCUGGAUCACCUCCUUUCU
>NZ_GG739926_647533195
UAAUGGGAGUUUGAUCCUGGCUCAGGAUGAACGCUGGCUACAGGCUUAACACAUGCAAGUCGAGGGACCGGCGCACGGGUGAGUAACGCGUAUCCAACCUUCCCGCGACCAAGGGAUAACCUGCCGAAAGGCAGACUAAUACCUUAUGUCCAAAGUCGGUCACGGAUGGGGAUGCGUCCGAUUAGCUUGUUGGCGGGGCAACGGCCCACCAAGGCAUCGAUCGGUAGGGGUUCUGAGAGGAAGGCCCCCCACACUGGAACUGAGACACGGUCCAGACUCCUACGGGAGGCAGCAGUGAGGAAUAUUGGUCAAUGGGCGGAAGCCUGAACCAGCCAAGUAGCGUGCAGGACGACGGCCUACGGGUUGUAAACUGCUUUUAUGCGGGGAUAUGCAGGUACCGCAUGAAUAAGGACCGGCUAAUUCCGUGCCAGCAGCCGCGGUAAUACGGAAGGUCCGGGCGUUAUCCGGAUUUAUUGGGUUUAAAGGGAGCGCAGGCCGCCGUGCAAGCGUGCCGUGAAAAGCAGCGGCCCAACCGCUGCCCUGCGGCGCGAACUGCUUGGCUUGAGUGCGCCGGAAGCGGGCGGAAUUCGUGGUGUAGCGGUGAAAUGCUUAGAUAUCACGAAGAACCCCGAUUGCGAAGGCAGCCCGCUGUGGCGACUGACGCUGAGGCUCGAAGGUGCGGGUAUCGAACAGGAUUAGAUACCCUGGUAGUCCGCACGGUAAACGAUGGAUACCCGCUGUCCGGCUCUGGGCGGCCAAGCGAAAGCGUUAAGUAUCCCACCUGGGGAGUACGCCGGCAACGGUGAAACUCAAAGGAAUUGACGGGGGCCCGCACAAGCGGAGGAACAUGUGGUUUAAUUCGAUGAUACGCGAGGAACCUUACCCGGGCUUGAAUUGUGAAGGUGCUGCAUGGUUGUCGUCAGCUCGUGCCGUGAGGUGUCGGCUCAAGUGCCAUAACGAGCGCAACCCCUCUCCGCAGUUGCCAUCGGCCGGGCACUCUGCGGACACUGCCGCCGCAAGGUGGAGGAAGGUGGGGAUGACGUCAAAUCAGCACGGCCCUUACGUCCGGGGCCACACACGUGUUACAAUGGCCGGCAGAGGGCUGUCCGCGCGCAAGUGCGGGUGAAUCCCCUCCGGUCCCAGUUCGGAUGGGGUCUGCAACCCGACCCCAGAAGCUGGAUUCGCUAGUAAUCGCGCAUCAGCCAUGGCGCGGUGAAUACGUUCCCGGGCCUUGUACACACCGCCCGUCAAGCCAUGAAAGCCGGGGGUGCCUGAAGUCCGUGUCGGCCUAGGGCAAAACCGGUGAUUGGGGCUAAGUCGUAACAAGGUAGCCGUACCGGAAGGUGCGGCUGGAACACCUCCUUUCU
>NZ_ACIZ01000148_643886127
AAUAUGGAGUUUGAUCCUGGCUCAGGAUGAACGCUGGCGGCGUGCCUAAUACAUGCAAGUCGAACGAGUGGCGGACGGGUGAGUAACACGUGGGUAACCUGCCCUUAAGUGGGGGAUAACAUUUGGAAACAGAUGCUAAUACCGCAUAAAGAAAGUCGCUUUUGGAUGGACCCGCGGCGUAUUAGCUAGUUGGUGAGGUAACGGCUCACCAAGGCAAUGAUACGUAGCCGAACUGAGAGGUUGAUCGGCCACAUUGGGACUGAGACACGGCCCAAACUCCUACGGGAGGCAGCAGUAGGGAAUCUUCCACAAUGGACGCAAGUCUGAUGGAGCAACGCCGCGUGAGUGAAGAAGGCUUUCGGGUCGUAAAACUCUGUUGUUGGAGAAGAUGACGGUAUCCAACCAGAAAGCCACGGCUAACUACGUGCCAGCAGCCGCGGUAAUACGUAGGUGGCAAGCGUUAUCCGGAUUUAUUGGGCGUAAAGCGAGCGCAGGCGGUUUUUUAAGUCUGAUGUGAAAGCCCUCGGCUUAACCGAGGAAGUGCAUCGGAAACUGGGAAACUUGAGUGCAGAAGAGGACAGUGGAACUCCAUGUGUAGCGGUGAAAUGCGUAGAUAUAUGGAAGAACACCAGUGGCGAAGGCGGCUGUCUGGUCUGACUGACGCUGAGGCUCGAAAGCAUGGGUAGCGAACAGGAUUAGAUACCCUGGUAGUCCAUGCCGUAAACGAUGAAUGCUAGGUGUUGGAGCUUCAGUGCCGCAGCUAACGCAUUAAGCAUUCCGCCUGGGGAGUACGACCGCAAGGUUGAAACUCAAAGGAAUUGACGGGGGCCCGCACAAGCGGUGGAGCAUGUGGUUUAAUUCGAAGCAACGCGAAGAACCUUACCAGGUCUUGACAUCGACAGGUGGUGCAUGGUUGUCGUCAGCUCGUGUCGUGAGAUGUUGGGUUAAGUCCCGCAACGAGCGCAACCCUUAUGACUAGUUGCCAGCAUGGGCACUCUAGUAAGACUGCCGGUGACAAACCGGAGGAAGGUGGGGAUGACGUCAAAUCAUCAUGCCCCUUAUGACCUGGGCUACACACGUGCUACAAUGGAUGGCAACGAGUUGCGAGACCGCGAGGUCAAGCUAAUCUCUUCCAUUCUCAGUUCGGAUGUAGGCUGCAACUCGCCUACAGAAGUCGGAAUCGCUAGUAAUCGCGGAUCAGCACGCCGCGGUGAAUACGUUCCCGGGCCUUGUACACACCGCCCGUCACACCAUGAGAGUUUGUAACACCCGAAGCCGGUGCGUAGCGAGCCGUCUAAGGUGGGACAAAUGAUUAGGGUGAAGUCGUAACAAGGUAGCCGUAGGAGAACCUGCGGCUGGAUCACCUCCUUUCU"""
test_query = test_query.splitlines()

if __name__ == '__main__':
    main()
