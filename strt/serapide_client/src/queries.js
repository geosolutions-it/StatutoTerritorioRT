import gql from "graphql-tag";

export const CREA_PIANO_PAGE = gql`
query CreaPianoPage{
    enti{
        edges{
            node{
                name
                code
                role
                type{
                    tipo: name
                }
            }
        }
    }
    tipologiaPiano{
        value
        label
      }
}
`
export const CREA_PIANO= gql`mutation CreatePiano($input: CreatePianoInput!) {
    createPiano(input: $input) {
        nuovoPiano {
            ente {
            code
            }
            codice
            tipologia
            dataCreazione
      }
    }
  }
`
export const GET_PIANI = gql`
query getPiani($faseCodice: String){
    piani(fase_Codice: $faseCodice){
        edges{
            node{
              codice
              tipo: tipologia
              descrizione
              lastUpdate
              fase{
                nome
                codice
                descrizione
              }
            }
          }
        }
}
`

