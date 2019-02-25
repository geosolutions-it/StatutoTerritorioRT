/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Button} from 'reactstrap'

export default ({ id, confirm , closeToast, label = "Elimina risorsa?" }) => {
    function handleClick(){
        confirm(id); 
        closeToast();
    }
    return (
      <div  className="px-1 text-dark d-flex  justify-content-around align-items-center">
        
         <span className="pr-1">{label}</span> <Button style={{fontSize: "0.7rem"}} color="danger"  onClick={handleClick}>Conferma</Button>
        
      </div>
    );
  }

