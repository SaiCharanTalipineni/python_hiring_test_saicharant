import pandas as pd

#- functions to calculate the scores
def avg(score):
    return round((score['H']) / score['AB'], 3)

def obp(score):
    return round((score['H'] + score['BB'] + score['HBP']) / (score['AB'] + score['BB'] + score['HBP'] + score['SF']), 3)

def slg(score):
    return round((score['H'] + score['2B'] + score['3B']*2 + score['HR']*3) / score['AB'], 3)

def ops(score):
    return round((score['H'] + score['BB'] + score['HBP']) / (score['AB'] + score['BB'] + score['HBP'] +
                score['SF']) + (score['H'] + score['2B'] + score['3B']*2 + score['HR']*3) / score['AB'], 3)


#- function to create a dataframe of scores and melting wide data to long data frame
def calculate(filtSum, oppos):
    req_df = pd.DataFrame(index=filtSum.index)
    req_df['AVG'] = filtSum.apply(avg, axis=1)
    req_df['OBP'] = filtSum.apply(obp, axis=1)
    req_df['SLG'] = filtSum.apply(slg, axis=1)
    req_df['OPS'] = filtSum.apply(ops, axis=1)
    req_df['SubjectId'] = filtSum.index
    req_df['Subject'] = filtSum.index.name
    req_df['Split']   = oppos
    req_df_melt = pd.melt(req_df, id_vars = ['Subject','SubjectId', 'Split'], value_vars=['AVG', 'OBP', 'SLG', 'OPS'])
    req_df_melt.rename(index=str, columns={"variable": "Stat"}, inplace =True)
    return req_df_melt


#- function to filter and sum the data with PA>=25
def filterSum(pitchData, i):
    if i == 'HitterId':
        filt_df_l = pitchData[['HitterId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.PitcherSide =='L']
        filt_df_r = pitchData[['HitterId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.PitcherSide =='R']
    if i == 'HitterTeamId':
        filt_df_l = pitchData[['HitterTeamId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.PitcherSide =='L']
        filt_df_r = pitchData[['HitterTeamId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.PitcherSide =='R']
    if i == 'PitcherId':
        filt_df_l = pitchData[['PitcherId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.HitterSide =='L']
        filt_df_r = pitchData[['PitcherId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.HitterSide =='R']
    if i == 'PitcherTeamId':
        filt_df_l = pitchData[['PitcherTeamId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.HitterSide =='L']
        filt_df_r = pitchData[['PitcherTeamId','PA', 'AB', 'H', '2B', '3B', 'HR', 'BB', 'SF','HBP']][pitchData.HitterSide =='R']
               
    filt_sum_l = filt_df_l.groupby(i).filter(lambda s: s.sum()['PA'] >= 25).groupby(i).sum()
    filt_sum_r = filt_df_r.groupby(i).filter(lambda s: s.sum()['PA'] >= 25).groupby(i).sum()
    return filt_sum_l, filt_sum_r
        
#- main function and where rows are concatenated to form a csv file
def main():
    pitchData = pd.read_csv('data/raw/pitchdata.csv') 
    Subject = ['HitterId', 'HitterTeamId', 'PitcherId', 'PitcherTeamId']
    
    output_list = []
    for i in Subject:
        filtSum_l, filtSum_r = filterSum(pitchData, i)
        if i == 'HitterId' or i == 'HitterTeamId':
            Split = ['vs LHP', 'vs RHP']
        else: Split = ['vs LHH', 'vs RHH']
        output_df = pd.concat([calculate(filtSum_l, Split[0]), calculate(filtSum_r, Split[1])])
        output_list.append(output_df)
        
    final_df = pd.concat(output_list)
    final_df = final_df[['SubjectId', 'Stat', 'Split', 'Subject', 'value']]

    final_df = final_df.sort_values(['SubjectId', 'Stat', 'Split', 'Subject'], ascending=True)
    final_df.rename(index=str, columns={"value": "Value"}, inplace =True)
    final_df.to_csv('data/processed/output.csv', index=False)
    
if __name__ == '__main__':
    main()