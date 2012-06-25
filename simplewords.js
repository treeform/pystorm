
function __keys(obj) {
    var result = [];
    var k;
    for ( k in obj ) {
        result.push(k);
    }    
    return result;
}




function __len(container) {
        if (container instanceof Array) {
            return container.length;
        }
        var i;
        var count = 0;
        for (i in container) {
            count++;
        }
        return count;
}





function Generator(container) {
        var isarray = (container instanceof Array);
        var isstring = (typeof(container) == 'string');
        if (container.__iter__) {
                this.values = [];
                this.iterator = container.__iter__();
        } else if (isarray || isstring) {
                this.values = container;
        } else {
                this.values = [];
                for(key in container) {
                        this.values.push(key);
                }
        }
        this.index = 0;
}

Generator.prototype.nextValue = function() {
        if (this.iterator) {
                try {
                        return this.iterator.next();
                } catch( e ) {
                        this.iterator_exhausted = true;
                        return null;
                }
        }
        else if (this.index < this.values.length) {
                return this.values[this.index++];
        } else {
                this.index++;
                return null;
        }
}

Generator.prototype.hadMore = function() {
        if (this.iterator_exhausted) {
                return false;
        }
        return (this.index-1) < this.values.length;
}






function __in(item,container) {
        if (container instanceof Array) {
            return container.indexOf(item) != -1;
        }
        return item in container;
}


// generated by pystorm from simplewords.py


var __name__ = '__main__';


words='able about account acid across act addition adjustment advertisement after again against agreement air all almost among amount amusement and angle angry animal answer ant any apparatus apple approval arch argument arm army art as at attack attempt attention attraction authority automatic awake baby back bad bag balance ball band base basin basket bath be beautiful because bed bee before behaviour belief bell bent berry between bird birth bit bite bitter black blade blood blow blue board boat body boiling bone book boot bottle box boy brain brake branch brass bread breath brick bridge bright broken brother brown brush bucket building bulb burn burst business but butter button by cake camera canvas card care carriage cart cat cause certain chain chalk chance change cheap cheese chemical chest chief chin church circle clean clear clock cloth cloud coal coat cold collar colour comb come comfort committee common company comparison competition complete complex condition connection conscious control cook copper copy cord cork cotton cough country cover cow crack credit crime cruel crush cry cup cup current curtain curve cushion damage danger dark daughter day dead dear death debt decision deep degree delicate dependent design desire destruction detail development different digestion direction dirty discovery discussion disease disgust distance distribution division do dog door doubt down drain drawer dress drink driving drop dry dust ear early earth east edge education effect egg elastic electric end engine enough equal error even event ever every example exchange existence expansion experience expert eye face fact fall false family far farm fat father fear feather feeble feeling female fertile fiction field fight finger fire first fish fixed flag flame flat flight floor flower fly fold food foolish foot for force fork form forward fowl frame free frequent friend from front fruit full future garden general get girl give glass glove go goat gold good government grain grass great green grey grip group growth guide gun hair hammer hand hanging happy harbour hard harmony hat hate have he head healthy hear hearing heart heat help high history hole hollow hook hope horn horse hospital hour house how humour I ice idea if ill important impulse in increase industry ink insect instrument insurance interest invention iron island jelly jewel join journey judge jump keep kettle key kick kind kiss knee knife knot knowledge land language last late laugh law lead leaf learning leather left leg let letter level library lift light like limit line linen lip liquid list little living lock long look loose loss loud love low machine make male man manager map mark market married mass match material may meal measure meat medical meeting memory metal middle military milk mind mine minute mist mixed money monkey month moon morning mother motion mountain mouth move much muscle music nail name narrow nation natural near necessary neck need needle nerve net new news night no noise normal north nose not note now number nut observation of off offer office oil old on only open operation opinion opposite or orange order organization ornament other out oven over owner page pain paint paper parallel parcel part past paste payment peace pen pencil person physical picture pig pin pipe place plane plant plate play please pleasure plough pocket point poison polish political poor porter position possible pot potato powder power present price print prison private probable process produce profit property prose protest public pull pump punishment purpose push put quality question quick quiet quite rail rain range rat rate ray reaction reading ready reason receipt record red regret regular relation religion representative request respect responsible rest reward rhythm rice right ring river road rod roll roof room root rough round rub rule run sad safe sail salt same sand say scale school science scissors screw sea seat second secret secretary see seed seem selection self send sense separate serious servant shade shake shame sharp sheep shelf ship shirt shock shoe short shut side sign silk silver simple sister size skin skirt sky sleep slip slope slow small smash smell smile smoke smooth snake sneeze snow so soap society sock soft solid some son song sort sound soup south space spade special sponge spoon spring square stage stamp star start statement station steam steel stem step stick sticky stiff still stitch stocking stomach stone stop store story straight strange street stretch strong structure substance such sudden sugar suggestion summer sun support surprise sweet swim system table tail take talk tall taste tax teaching tendency test than that the then theory there thick thin thing this thought thread throat through through thumb thunder ticket tight till time tin tired to toe together tomorrow tongue tooth top touch town trade train transport tray tree trick trouble trousers true turn twist umbrella under unit up use value verse very vessel view violent voice waiting walk wall war warm wash waste watch water wave wax way weather week weight well west wet wheel when where while whip whistle white who why wide will wind window wine wing winter wire wise with woman wood wool word work worm wound writing wrong year yellow yes yesterday you young toor';
function random_choice(l)  {
    return (l[Math.floor((Math.random() * __len(l)))]);
}

end='!';

c1=end;

c2=end;

table={};


container_pystorm_1=words.split(/\s+/);
var generator_pystorm_2 = new Generator(container_pystorm_1);
for(word=generator_pystorm_2.nextValue();generator_pystorm_2.hadMore();word=generator_pystorm_2.nextValue()) {
    
    
    container_pystorm_3=word + end;
    var generator_pystorm_4 = new Generator(container_pystorm_3);
    for(c=generator_pystorm_4.nextValue();generator_pystorm_4.hadMore();c=generator_pystorm_4.nextValue()) {
        
        k=c1 + c2;
        if (__in(k,table)) {
            
            (table[k])=(table[k]) + c;
        }else  {
            
            (table[k])=c;
        }
        
        c1=c2;
        
        c2=c;
    }
}
function genword()  {
    var t;
    t=random_choice(__keys(table));
    var c1;
    c1=t[0];
    var c2;
    c2=t[1];
    var word;
    word=[];
    while(true) {
        var c;
        c=random_choice((table[(c1 + c2)]));
        if (c != end) {
            word.push(c);
            var c1;
            c1=c2;
            var c2;
            c2=c;
        }else  {
            if (__len(word) > 6) {
                break;
            }else  {
                var t;
                t=random_choice(__keys(table));
                var c1;
                c1=t[0];
                var c2;
                c2=t[1];
            }
        }
    }
    var word;
    word=word.join('');
    if (__len(word) > 10) {
        var word;
        word=word.slice(0,10);
    }
    return word;
}
if (__name__ == '__main__') {
    
    a={};
    
    c=0;
    
    ws=[];
    
    N=100000;
    
    for(i=0;i<N;i+=1) {
        
        w=genword();
        console.log(String(w));
        if (__in(w,a)) {
            
            c += 1;
            ws.push(w);
        }else  {
            
            (a[w])=true;
        }
    }
    console.log();
    console.log(String(c)+ " " +String('collisions per')+ " " +String(N)+ " " +String('words'));
    console.log(String('Collision words:')+ " " +String(ws.join('')));
}

