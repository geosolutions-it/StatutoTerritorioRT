import { format, parseISO} from 'date-fns'
import { it } from 'date-fns/locale'

export const getEnteLabel = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `${tipoente} di ${name}`
export const getEnteLabelID = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `ID ${tipoente} ${code}`
export const getPianoLabel = (tipo = "") => (tipo === "VARIANTE" ? tipo.toLowerCase() : `piano ${tipo.toLowerCase()}`)
export const formatDate = (date) => format(parseISO(date) , "iiii do MMMM yyyy", {locale: it})
export const fasi = [ "draft", "anagrafica", "avvio", "adozione", "approvazione", "pubblicazione"]