import csv


class CSV_Service():

    def get_dictionary_from_csv(self, filename):
        parsed_dictionary = {}
        filename = filename

        with open(filename, newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')

            i = 0
            """
            with open('yourfile.csv', 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=',')
                rows = list(csv_reader)  # read all rows into a list
                rows.reverse()  # reverse the list
            """

            rows = list(csv_reader)
            for line in reversed(rows):

                
                atm_date = ''
                receiver_account = ''
                location = ''
                location2 = ''
                transaction_reference = ''

                #print('Transaction ID: ', end='')
                #print('1')

                account = line['Posted Account'].split(' - ')
                #print('Sort Code: ', end='')
                #print(account[0])
                #print('Account Number: ', end='')
                #print(account[1])
                account_number = account[1]
                sort_code = account[0]

                #print('Date: ', end='')
                #print(line[' Posted Transactions Date'])
                transaction_date = line[' Posted Transactions Date']

                if line[' Credit Amount']:
                    amount2 = line[' Credit Amount']
                    type = 'Credit'
                else:
                    amount2 = line[' Debit Amount']
                    type = 'Debit'
                amount = amount2.replace(',','')
                
                #print('Amount: ', end='')
                #print(amount)

                #print('Type: ', end='')
                #print(type)
                
                currency = line['Local Currency']

                balance = line['Balance']

                if 'D/D' in line[' Description1']:
                    card_function = 'Direct Debit'
                    receiver_name = line[' Description1'].replace('D/D ','')
                    receiver_account = line[' Description2']
                    #print('Receiver Account: ', end='')
                    #print(receiver_account)
                elif 'VDP' in line[' Description1']:
                    card_function = 'Retail payment with Visa Debit'
                    receiver_name = line[' Description1'].replace('VDP-','')
                elif 'VDC' in line[' Description1']:
                    card_function = 'Contactless Visa Debit'
                    receiver_name = line[' Description1'].replace('VDC-','')
                elif 'VDA' in line[' Description1']:
                    card_function = 'ATM'
                    receiver_name = ''
                    location = line[' Description1'].replace('VDA-','')
                    #print('Location: ', end='')
                    #print(location)
                    location2 = line[' Description2']
                    #print('Location (cont): ', end='')
                    #print(location2)
                    atm_date = line[' Description3']
                    #print('ATM Date/Time: ', end='')
                    #print(atm_date)
                elif '*MOBI' in line[' Description1']:
                    card_function = 'Transfer via Mobile App'
                    receiver_name = line[' Description1'].replace('*MOBI ','')
                elif 'STAMP DUTY' in line[' Description1']:
                    card_function = 'Card Stamp Duty Fee'
                    receiver_name = line[' Description1'].replace('STAMP DUTY ','')
                elif 'NO FEES - MORTGAGE' in line[' Description1']:
                    card_function = 'Mortgage Payment'
                    receiver_name = ''
                elif 'FEE-QTR TO' in line[' Description1']:
                    card_function = 'Quarterly Fee'
                    receiver_name = line[' Description1'].replace('FEE-QTR TO ','')
                else:
                    card_function = 'Deposit'
                    receiver_name = ''
                    transaction_reference = line[' Description1']
                    #print('Reference: ', end='')
                    #print(line[' Description1'])


                #print('Card Function: ', end='')
                #print(card_function)
                #print('Receiver Name: ', end='')
                #print(receiver_name)
                #print('')
                #print('')


                parsed_dictionary[i] = { 'transaction_id' : i,
                                        'file_name' : filename,
                                        'account_number' : account_number,
                                        'sort_code' : sort_code,
                                        'transaction_date' : transaction_date,
                                        'atm_date' : atm_date,
                                        'currency' : currency,
                                        'amount' : amount,
                                        'balance' : balance,
                                        'type' : type,
                                        'card_function' : card_function,
                                        'receiver_name' : receiver_name,
                                        'receiver_account' : receiver_account,
                                        'location' : location,
                                        'location2' : location2,
                                        'transaction_reference' : transaction_reference,
                                        }
                i+=1

        return parsed_dictionary

            #print(csv_file)