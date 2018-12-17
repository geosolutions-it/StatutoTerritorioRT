/** 
 * Moked data waiting for Alessio beckend
*/

const piani = [{
    notifica: "urgente", // per un piano possono esserci più notifiche
    nome: "Disposizini concernenti la tutela e la disciplina comune del patrimonio territoriale",
    tipo: "piano operativo",
    ultima_modifica: "22/10/2018",
    codice: "PO 010119",
    stato: "adozione",
    rup: "Virginia Raggi"},{
    notifica: "importante",
    nome: "Disposizini concernenti la tutela e la disciplina comune del patrimonio territoriale",
    tipo: "piano operativo",
    ultima_modifica: "22/11/2018",
    codice: "PO 010120",
    stato: "avvio",
    rup: "Virginia Raggi"}
]
const user = {
    nome: "Virginia Nardi",
    organizzazione: "Comune di Scandicci",
    ruolo: "rup"
}
const messaggi = [{
    id: 1,
    data: "13/12/2018",
    from: {nome: "Leonardo Scalzi", organizzazione: "Comune di Scandicci"},
    testo: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas volutpat, lectus ac finibus dictum, lorem odio convallis nisi, vel rhoncus lorem ante nec tellus. Duis auctor pretium felis, vitae vestibulum quam blandit ut."

},
{
    id: 2,
    data: "8/12/2018",
    from: {nome: "Amaranta Bianchi", organizzazione: "Regione Toscana"},
    testo: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas volutpat, lectus ac finibus dictum, lorem odio convallis nisi, vel rhoncus lorem ante nec tellus. Duis auctor pretium felis, vitae vestibulum quam blandit ut."
}]

export {piani, user, messaggi}