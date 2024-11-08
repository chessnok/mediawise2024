import React from 'react';
import '../DinoMasterpiece.css';

const DinoMasterpiece = () => {
    return (
        <div className="dino-container">
            <div className="dino-art">
                <div className="dino-body">
                    <div className="dino-head">
                        <div className="dino-eye"></div>
                        <div className="dino-mouth"></div>
                    </div>
                    <div className="dino-arms">
                        <div className="dino-arm"></div>
                        <div className="dino-arm"></div>
                    </div>
                    <div className="dino-legs">
                        <div className="dino-leg"></div>
                        <div className="dino-leg"></div>
                    </div>
                    <div className="dino-tail"></div>
                </div>
            </div>
            <h2 className="dino-title">DinoMasterpiece</h2>
        </div>
    );
};

export default DinoMasterpiece;
