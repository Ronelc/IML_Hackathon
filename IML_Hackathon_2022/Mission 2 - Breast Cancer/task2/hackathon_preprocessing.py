import pandas as pd
import re
import warnings

warnings.simplefilter(action='ignore', category=Warning)

# dictionary from y0 label to number
y0_label_to_num = {'BON - Bones': 0, 'LYM - Lymph nodes': 1,
                   'HEP - Hepatic': 2, 'PUL - Pulmonary': 3,
                   'PLE - Pleura': 4, 'SKI - Skin': 5, 'BRA - Brain': 6,
                   'MAR - Bone Marrow': 7,
                   'ADR - Adrenals': 8, 'PER - Peritoneum': 9,
                   'OTH - Other': 10}
# dictionary from y0 number to label
y0_num_to_label = {0: 'BON - Bones', 1: 'LYM - Lymph nodes',
                   2: 'HEP - Hepatic', 3: 'PUL - Pulmonary',
                   4: 'PLE - Pleura', 5: 'SKI - Skin', 6: 'BRA - Brain',
                   7: 'MAR - Bone Marrow',
                   8: 'ADR - Adrenals', 9: 'PER - Peritoneum',
                   10: 'OTH - Other'}


# find number in front of percentage sign
def find_percentage_num(value):
    idx = value.find('%')
    i = idx - 1
    while i >= 0:
        if value[i].isnumeric():
            if i != 0:
                i -= 1
            else:
                break
        else:
            i += 1
            break
    if i != idx:
        return min(100, int(value[i:idx]))


# parse through er column
def parse_er(value):
    """
    -1 - unknown, 0 - negative, 100 - positive
    percentage , 0 - 8
    :param value:
    :return:
    """
    value = str(value)
    positive = ["(+)", "חיובי", "+", "חיובי", "strongly", "p0s", "jhuch",
                "p", "high", "+++", "++"]
    weak_pos = ["moderat. pos", "Moder. pos", "Intermediate positive",
                "Weakly pos", "interm. pos", "חיובי חלש", "mild positive", ]
    negative = ["NETGATIVE", "שלילי", "(-)", "-", "NEG", "begative",
                "NEGATIVE", "beg", "nge", "((-)"]
    if value == "nan":
        return -1
    if '%' in value:
        return find_percentage_num(value)
    if value in weak_pos or "weak" in value:
        return 50
    elif ("pos" in value and "neg" in value) or (
            "POS" in value and "NEG" in value):
        return -1
    elif value in negative or "neg" in value or "Neg" in value:
        return 0
    elif value in positive or "po" in value or "Pos" in value or "POS" in value:
        return 100
    nums = re.findall('\d+', value)
    if len(nums) != 0:
        num = int(nums[0])
        if num <= 0:
            return -1
        elif num >= 100:
            return 100
        return num
    elif ("pos" in value and "neg" in value) or (
            "POS" in value and "NEG" in value):
        return -1
    else:
        return -1


# parse through her2_gene column
def parse_her2_gene(value):
    """
    Her2 values are negative(-1), borderline(0), positive(1).
    so first we change everything to neg/bord/pos and then factorize
    :param value:
    :return:
    """
    value = str(value).lower()
    NEGATIVE_OPTIONS = ['neg', 'negative', '1', '0', '-', 'naeg', 'nefative',
                        'akhkh', 'akhah', 'begative', 'שלילי',
                        'heg', 'nec']
    BORDERLINE_OPTIONS = ['borderline', '2', 'בינוני', '?']
    POSITIVE_OPTIONS = ['pos', 'positive', '+3', '3', '+']
    if value in NEGATIVE_OPTIONS or \
            'neg' in value or 'negative' in value:
        return -1
    if value in BORDERLINE_OPTIONS or 'borderline' in value:
        return 0
    if value in POSITIVE_OPTIONS or '+3' in value or \
            'po' in value or 'חיובי' in value:
        return 1
    # DONT CHANGE ORDER, THIS CHECK COMES AFTER!
    if "(-)" in value or '(+1)' in value:
        return -1
    if "+2" in value or "2+" in value:
        return 0
    if "(+)" in value:
        return 1
    if '2' in value or 'in' in value or '?' in value or 'amplified' in value or 'equiv' in value:
        return 0
    if '1' in value or '-' in value or '_' in value:
        return -1
    if '3' in value or '+' in value:
        return 1
    return -1


# parse through KI67 column
def parse_KI67_protein(value):
    months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
              "jul": 7,
              "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    greek_letters = ["iv", "iii", "ii", "i"]
    greek_to_num = {"i": 5, "ii": 15, "iii": 35, "iv": 70}
    scores = {"1": 5, "2": 15, "3": 35, "4": 70}
    words_to_num = {"low": 5, "inter": 23, "int": 23, "high": 50, "נמוך": 5}
    empty = {"nan", "?", "no", "negative", "notdone", "pos", "%", "false"}
    value = str(value).lower().replace(' ', '').replace('=', '%')
    if value in empty:
        return None
    if '%' in value:
        return find_percentage_num(value)
    for month in months:
        if month in value:
            return months[month]
    if "score" in value:
        for greek in greek_letters:
            if greek in value:
                return greek_to_num[greek]
        for score in scores:
            return scores[score]
    for word in words_to_num:
        if word in value:
            return words_to_num[word]
    return min(abs(int(re.sub("[^0-9]", "", value))), 100)


# parse through pr column
def parse_pr(value):
    """
    -1 - unknown, 0 - negative, 100 - positive
    percentage , 0 - 8
    :param value:
    :return:
    """
    empty = {"nan", "?", "notdone", "%"}
    negative = {"neg", "negative", "eg", "non", "false", "nag", "akhah",
                "שלילי", "(-)", "nrg", "akhkh", "nec", "no",
                "nef", "-", "nd", "nfg"}
    positive = {"pos", "positive", "po", "yes", "yeah", "חיובי", "true", "(+)",
                "+"}
    value = str(value).lower().replace(' ', '').replace('=', '%')
    if value in empty:
        return -1
    if "pos" in value and "neg" in value:
        return -1
    if '%' in value:
        return find_percentage_num(value)
    for i in negative:
        if i in str(value).lower():
            return 0
    for i in positive:
        if i in str(value).lower():
            return 100
    if str(value).isdigit():
        if 0 <= int(value) <= 8:
            return value
    else:
        return None


# parse through Lvi column
def parse_Lvi(value):
    positive = ["+", "(+)", "pos", "yes", "extensive", "YES"]
    negative = ["-", "(-)", "neg", "no", "not", "NO"]
    if value in positive:
        return 1
    elif value in negative:
        return 2
    elif str(value).lower() == "micropapilary variant":
        return 3
    else:
        return None


# receives string "<NUM>_Onco" and returns <NUM> as int
def parse_user_name(string_to_parse):
    firstIndex = string_to_parse.find("_")
    return int(string_to_parse[:firstIndex])


# parse through metastases column
def parse_metastases(response):
    y = []
    for label in y0_label_to_num:
        if label in response:
            y.append(y0_label_to_num[label])
    return y


# distance between two given dates
def date_distance(date1, date2):
    if not (date1 and date2):
        return 0
    return max(date1, date2) - min(date1, date2)


class PreProcess:
    def __init__(self, train_filename, test_filename, label0_filename,
                 label1_filename):
        self.df = pd.read_csv(train_filename, dtype=object, encoding='utf-8')
        self.test_data = pd.read_csv(test_filename, dtype=object,
                                     encoding='utf-8')
        self.test_size = self.test_data.shape[0]
        self.y1 = pd.read_csv(label1_filename)
        self.y0 = pd.read_csv(label0_filename)
        for i in [self.df, self.y1, self.y0, self.test_data]:
            i.columns = [x.replace("אבחנה-", '').replace(" ", '_').lower() for
                         x in i.columns]
        self.test_unique_and_counts = self.test_data['id-hushed_internalpatientid'].value_counts(sort=False)
        self.df = pd.concat([self.df, self.test_data], ignore_index=True)

    def process(self):
        self.process_y()
        self.df = pd.concat([self.df, self.y0, self.y1], axis=1)
        # factorize
        self.factorize_data()
        self.df["basic_stage"].replace("Null", "p - Pathological",
                                       inplace=True)
        self.df['basic_stage'] = pd.factorize(self.df['basic_stage'])[0]
        # process dates
        self.process_dates()
        # parse columns row by row
        self.apply_data()
        # fill NA by median
        self.df = self.df.fillna(self.df.median())
        # group data by ID
        dropped_cols = ['tumor_size', 'location_of_distal_metastases',
                        'ivi_-lymphovascular_invasion',
                        'ki67_protein',
                        'lymphatic_penetration',
                        'm_-metastases_mark_(tnm)',
                        'margin_type',
                        'side',
                        'stage',
                        'surgery_name2',
                        'surgery_name1',
                        'surgery_name3',
                        'surgery_sum',
                        't_-tumor_mark_(tnm)',
                        'tumor_depth',
                        'tumor_width',
                        'er',
                        'pr'
                        # '_form_name',
                        # '_hospital',
                        # 'user_name'
                        ]
        self.groupby_data()
        # drop data
        self.df.drop(dropped_cols,
                     inplace=True, axis=1)
        self.test_data.drop(dropped_cols,
                            inplace=True, axis=1)

    def factorize_data(self):
        factorize_lst = ['_form_name',
                         'surgery_before_or_after-actual_activity',
                         '_hospital',
                         'user_name', 'margin_type', 'side', 'surgery_name1',
                         'surgery_name2', 'surgery_name3',
                         'histological_diagnosis', 'lymphatic_penetration',
                         'm_-metastases_mark_(tnm)',
                         'n_-lymph_nodes_mark_(tnm)', 't_-tumor_mark_(tnm)',
                         'histopatological_degree', 'stage']
        for i in factorize_lst:
            self.df[i] = pd.factorize(self.df[i])[0]

    # all the apply functions needed for pre-processing
    def apply_data(self):
        self.df['ki67_protein'] = self.df.apply(
            lambda x: parse_KI67_protein(x['ki67_protein']), axis=1)
        self.df['ivi_-lymphovascular_invasion'] = self.df.apply(
            lambda x: parse_Lvi(x['ivi_-lymphovascular_invasion']),
            axis=1)
        self.df['her2'] = self.df.apply(lambda x: parse_her2_gene(x['her2']),
                                        axis=1)
        self.df['pr'] = self.df.apply(lambda x: parse_pr(x['pr']), axis=1)
        self.df['er'] = self.df.apply(lambda x: parse_er(x['er']), axis=1)

    # all the groupby needed for pre-processing
    def groupby_data(self):
        self.test_data = self.df[self.df.shape[0] - self.test_size:]
        self.df = self.df[:self.df.shape[0] - self.test_size]
        all_unique_and_counts = self.df['id-hushed_internalpatientid'].value_counts(sort=False)
        self.df = self.df.groupby(['id-hushed_internalpatientid'],
                                  sort=False).first()
        self.test_data = self.test_data.groupby(['id-hushed_internalpatientid'],
                                                sort=False).first()
        self.df = pd.concat([self.df, all_unique_and_counts], axis=1)
        self.test_data = pd.concat([self.test_data, self.test_unique_and_counts], axis=1)

        self.y0 = self.df['location_of_distal_metastases']
        self.y1 = self.df['tumor_size']

    # all the dates needed for pre-processing
    def process_dates(self):
        date_columns = ['diagnosis_date', 'surgery_date1', 'surgery_date2', 'surgery_date3',
                        'surgery_before_or_after-activity_date']
        # for col in date_columns:
        #     self.df[col] = self.df[col].replace("Unknown", None)
        #     self.df[col] = pd.to_datetime(self.df[col])
        # self.df["surgery_before_to_diag"] = self.df.apply(
        #     lambda x: date_distance(x["diagnosis_date"], x['surgery_before_or_after-activity_date']), axis=1).dt.days
        # self.df["diag_to_surg1"] = self.df.apply(
        #     lambda x: date_distance(x["diagnosis_date"], x['surgery_date1']), axis=1).dt.days
        # self.df["surg1_to_surg2"] = self.df.apply(
        #     lambda x: date_distance(x['surgery_date1'], x['surgery_date2']), axis=1).dt.days
        # self.df["surg2_to_surg3"] = self.df.apply(
        #     lambda x: date_distance(x['surgery_date2'], x['surgery_date3']), axis=1).dt.days
        self.df.drop(date_columns, inplace=True, axis=1)

    def get_unique_and_counts(self):
        return self.test_unique_and_counts

    def process_y(self):
        self.y0 = self.y0['location_of_distal_metastases']
        self.y0 = self.y0.apply(parse_metastases)
        self.y1 = self.y1['tumor_size']

    def get_train_test(self):
        return self.df, self.test_data, self.y0, self.y1
