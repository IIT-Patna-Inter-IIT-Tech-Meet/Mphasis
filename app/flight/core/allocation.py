import re
import math

class BaseReallocation:
    def __init__(self, get_pnr_fn, get_alt_flights_fn, get_cancled_fn) -> None:
        self.map_cabin={ 'F':'F','P':'F','C':'B','J':'B','Z':'B','Q':'P','R':'P','S':'P','T':'P','H':'P','M':'P',
          'Y':'E', 'A':'E', 'B':'E', 'D':'E', 'E':'E', 'G':'E', 'I':'E', 'K':'E', 'L':'E', 'N':'E', 'O':'E',
           'U':'E', 'V':'E','W':'E','X':'E'}
        self.cabins=['F','B','P','E']
        self.cabin_ind={'F':0 , 'B':1,'P':2,'E':3}

        self._preprocess_data(get_pnr_fn, get_alt_flights_fn, get_cancled_fn)

    def _preprocess_data(self, get_pnrs,get_alt_flights,get_cancled):
        cancel=get_cancled()
        pnr={}
        alt_flight={}
        # pnr_flight={}
        for f in cancel['data']:
            pnr[f['flight_id']]=get_pnrs(f['flight_id'])["data"]
            alt=get_alt_flights(f['flight_id'])
            f2=[]
            for flight in alt['data']:
                f3={}
                f3['flight_id']=flight['flight_id']
                f3['delay']=flight['delay']
                f3['flight_time']=flight['flight_time']
                f3['F']=0
                f3['B']=0
                f3['P']=0
                f3['E']=0
    #           print()
                for key in self.map_cabin:
                    if key in flight['avilable_seats']:
                        f3[self.map_cabin[key]]+=flight['avilable_seats'][key]
                f2.append(f3)
            f4=[]
            for flight in alt['c_flights']:
                f5=[]
                for fl in flight:
                    f3={}
                    f3['flight_id']=fl['flight_id']
                    f3['delay']=fl['delay']
                    f3['flight_time']=fl['flight_time']
                    f3['F']=0
                    f3['B']=0
                    f3['P']=0
                    f3['E']=0
        #         print()
                    for key in self.map_cabin:
                        if key in fl['avilable_seats']:
                            f3[self.map_cabin[key]]+=fl['avilable_seats'][key]
                    f5.append(f3)
                f4.append(f5)
            f6=[]
            for flight in alt['t_flights']:
                f7=[]
                for fl in flight:
                    f3={}
                    f3['flight_id']=fl['flight_id']
                    f3['delay']=fl['delay']
                    f3['flight_time']=fl['flight_time']
                    f3['F']=0
                    f3['B']=0
                    f3['P']=0
                    f3['E']=0
        #         print()
                    for key in self.map_cabin:
                        if key in fl['avilable_seats']:
                            f3[self.map_cabin[key]]+=fl['avilable_seats'][key]
                    f7.append(f3)
                f6.append(f7)
        #     print(f['flight_id'])
            alt_flight[f['flight_id']]={'n_flights':f2,'c_flights':f4,'t_flights':f6}
        self.pnr, self.alt_flight = pnr,alt_flight

    @staticmethod
    def get_delay_cost(delay_str):
        comp = delay_str.split(", ")
        hours=0
        minutes=0
        seconds=0
        total_hours_from_days=0
        # Extract hours, minutes, and seconds from the time string
        if len(comp)==1:
            hours, minutes, seconds = map(int, comp[0].split(":"))
            total_hours_from_days=0
        else:
            days, time_str = delay_str.split(", ")
            hours, minutes, seconds = map(int, comp[1].split(":"))
            total_hours_from_days = int(comp[0].split()[0]) * 24
        time = total_hours_from_days + hours
        if(minutes>30):
            time+=1
        time = math.exp(time/3)
        return time
    
    @staticmethod
    def get_layoff_cost(delay_str):
        comp = delay_str.split(", ")
        hours=0
        minutes=0
        seconds=0
        total_hours_from_days=0
        # Extract hours, minutes, and seconds from the time string
        if len(comp)==1:
            hours, minutes, seconds = map(int, comp[0].split(":"))
            total_hours_from_days=0
        else:
            days, time_str = delay_str.split(", ")
            hours, minutes, seconds = map(int, comp[1].split(":"))
            total_hours_from_days = int(comp[0].split()[0]) * 24
        time = total_hours_from_days + hours
        if(minutes>30):
            time+=1
        time = math.exp(time/2.5)
        return time

    @staticmethod
    def get_flight_time_score(d,s):
        delay_str = s
        comp = delay_str.split(", ")
        hours=0
        minutes=0
        seconds=0
        total_hours_from_days=0
        # Extract hours, minutes, and seconds from the time string
        if len(comp)==1:
            hours, minutes, seconds = map(int, comp[0].split(":"))
            total_hours_from_days=0
        else:
            days, time_str = delay_str.split(", ")
            hours, minutes, seconds = map(int, comp[1].split(":"))
            total_hours_from_days = int(comp[0].split()[0]) * 24
        time = total_hours_from_days + hours
        if(minutes>30):
            time+=1
        if d==0 :
            return 0
        elif(d>0):
            return d*math.exp(time/1.2)
        else:
            return (-d)*math.exp(time/1.5)

    def obj(self, flights,pnr):
        list_cost=[]
        cost_id = []
        n_flights=flights['n_flights']
        c_flights=flights['c_flights']
        t_flights=flights['t_flights']
        f_id=[-1]
        c_id=[-1]
        val=1e18
        c_up=3
        c_down=2
        temp_id=0
        cabin0=self.cabin_ind[self.map_cabin[pnr['class']]]
        for f in  n_flights:
    #         print(f)
    #         break
            cost=self.get_delay_cost(f['delay'])
                
            for i in self.cabins:
                if(f[i]<pnr['pax']+self.used_seat[f['flight_id']][i]):
                    continue
                d=self.cabin_ind[i]-cabin0
                c=self.get_flight_time_score(d,f['flight_time'])
    #             print(c+cost)
                list_cost.append(c+cost+1)
                cost_id.append([[f['flight_id']],[i]])
                if(c+cost<val):
                    val=c+cost
                    f_id=[f['flight_id']]
                    c_id=[i]
    #             temp_id+=1
    #     flight_no=temp_id/n_class
    #     class_no=temp_id%n_class
    #     print('kkkkkk')
        for f in c_flights:
            
    #         print(f[1]['delay'])
            cost=self.get_delay_cost(f[0]['delay'])+self.get_layoff_cost(f[1]['delay'])
            
            for i in self.cabins:
                for j in self.cabins:
                    if(f[0][i]<pnr['pax']+self.used_seat[f[0]['flight_id']][i] or f[1][j]<pnr['pax']+self.used_seat[f[0]['flight_id']][j]):
                        continue
                    d1=self.cabin_ind[i]-cabin0
                    d2=self.cabin_ind[j]-cabin0
                    c=self.get_flight_time_score(d1,f[0]['flight_time'])
                    c+=self.get_flight_time_score(d2,f[1]['flight_time'])
    #                 print(c+cost)
                    list_cost.append(c+cost+1)
                    cost_id.append([[f[0]['flight_id'],f[1]['flight_id']],[i,j]])
                    if(c+cost<val):
                        val=c+cost
                        f_id=[f[0]['flight_id'],f[1]['flight_id']]
                        c_id=[i,j]
                        
        for f in t_flights:
            
    #         print(f[1]['delay'])
            cost=self.get_delay_cost(f[0]['delay'])+self.get_layoff_cost(f[1]['delay'])+self.get_layoff_cost(f[2]['delay'])
            
            for i in self.cabins:
                for j in self.cabins:
                    for k in self.cabins:
                        if(f[0][i]<pnr['pax']+self.used_seat[f[0]['flight_id']][i] or f[1][j]<pnr['pax']+self.used_seat[f[1]['flight_id']][j]
                    or f[2][k]<pnr['pax']+self.used_seat[f[2]['flight_id']][k]):
                            continue
                        d1=self.cabin_ind[i]-cabin0
                        d2=self.cabin_ind[j]-cabin0
                        d3=self.cabin_ind[k]-cabin0
                        c=self.get_flight_time_score(d1,f[0]['flight_time'])
                        c+=self.get_flight_time_score(d2,f[1]['flight_time'])
                        c+=self.get_flight_time_score(d3,f[2]['flight_time'])
    #                 print(c+cost)
                        list_cost.append(c+cost+1)
                        cost_id.append([[f[0]['flight_id'],f[1]['flight_id'],f[2]['flight_id']],[i,j,k]])
                        if(c+cost<val):
                            val=c+cost
                            f_id=[f[0]['flight_id'],f[1]['flight_id'],f[2]['flight_id']]
                            c_id=[i,j,k]
            
        if val!=1e18:
            self.tot_cost+=val
        return f_id,c_id,val,list_cost,cost_id
    


class PnrReallocation(BaseReallocation):
    def __init__(self, get_pnr_fn, get_alt_flights_fn, get_cancled_fn) -> None:
        super().__init__(get_pnr_fn, get_alt_flights_fn, get_cancled_fn)
        
    def allocate(self) -> None:
        self.used_seat={}
        self.maximum_seat={}

        for i in self.alt_flight:
            for j in self.alt_flight[i]['n_flights']:
                self.used_seat[j['flight_id']]={'F':0,'B':0,'P':0,'E':0}
                self.maximum_seat[j['flight_id']]={'F':j['F'],'B':j['B'],'P':j['P'],'E':j['E']}
            for j in self.alt_flight[i]['c_flights']:
                self.used_seat[j[0]['flight_id']]={'F':0,'B':0,'P':0,'E':0}
                self.maximum_seat[j[0]['flight_id']]={'F':j[0]['F'],'B':j[0]['B'],'P':j[0]['P'],'E':j[0]['E']}
                self.used_seat[j[1]['flight_id']]={'F':0,'B':0,'P':0,'E':0}
                self.maximum_seat[j[1]['flight_id']]={'F':j[1]['F'],'B':j[1]['B'],'P':j[1]['P'],'E':j[1]['E']}
            for j in self.alt_flight[i]['t_flights']:
                self.used_seat[j[0]['flight_id']]={'F':0,'B':0,'P':0,'E':0}
                self.maximum_seat[j[0]['flight_id']]={'F':j[0]['F'],'B':j[0]['B'],'P':j[0]['P'],'E':j[0]['E']}
                self.used_seat[j[1]['flight_id']]={'F':0,'B':0,'P':0,'E':0}
                self.maximum_seat[j[1]['flight_id']]={'F':j[1]['F'],'B':j[1]['B'],'P':j[1]['P'],'E':j[1]['E']}
                self.used_seat[j[2]['flight_id']]={'F':0,'B':0,'P':0,'E':0}
                self.maximum_seat[j[2]['flight_id']]={'F':j[2]['F'],'B':j[2]['B'],'P':j[2]['P'],'E':j[2]['E']}

        
        sorted_pnr=[]
        for i in self.pnr:
            alloc={}
            for j in self.pnr[i]:
                alloc=j
                alloc['flight_id']=i
                sorted_pnr.append(alloc)
        sorted_pnr = sorted(sorted_pnr, key=lambda x: x['score'],reverse=True)

        self.allocated={}

        for i in sorted_pnr:
            self.allocated[i['pnr']]='NULL'

        self.tot_cost=0
    
        for i in sorted_pnr:
        #     print(i)
            f_id=i['flight_id']
            flight_id,cabin_id,cost,_,_=self.obj(self.alt_flight[f_id],i)
            # list_cost=self.obj(self.alt_flight[f_id],i)
        #     break
        #     print(flight_id)
        #     print(cabin_id)
            if(len(flight_id)==3):
                self.allocated[i['pnr']]=[flight_id,cabin_id,cost]
                self.used_seat[flight_id[0]][cabin_id[0]]+=i['pax']
                self.used_seat[flight_id[1]][cabin_id[1]]+=i['pax']
                self.used_seat[flight_id[2]][cabin_id[2]]+=i['pax']
            elif(len(flight_id)==2):
                self.allocated[i['pnr']]=[flight_id,cabin_id,cost]
                self.used_seat[flight_id[0]][cabin_id[0]]+=i['pax']
                self.used_seat[flight_id[1]][cabin_id[1]]+=i['pax']
            elif(flight_id[0]!=-1):
                self.allocated[i['pnr']]=[flight_id[0],cabin_id[0],cost]
                self.used_seat[flight_id[0]][cabin_id[0]]+=i['pax']

        return self.allocated