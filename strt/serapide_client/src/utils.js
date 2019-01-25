

export const getEnteLabel = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `${tipoente} di ${name}`
export const getEnteLabelID = ({name = "", code, type: {tipoente = ""} ={}} = {}) => `ID ${tipoente} ${code}`