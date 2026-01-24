"""
Generador de Eventos Sintéticos de Señalización Móvil (SGSN-MME)

Este módulo genera eventos realistas de señalización de redes móviles incluyendo:
- Attach (initial, handover, periodic)
- Handover (X2, S1)
- Paging
- Detach
- Service Request

Uso:
    # Generar una sola vez
    python generator.py --mode once --events 10000
    
    # Ejecutar continuamente
    python generator.py --mode continuous --batch-size 1000 --interval 60

Autor: [Tu Nombre]
Fecha: Enero 2025
"""

import argparse
import json
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# =====================================================================
# CONFIGURACIÓN Y CONSTANTES
# =====================================================================

class EventType(Enum):
    """Tipos de eventos de señalización."""
    ATTACH = "attach"
    HANDOVER = "handover"
    PAGING = "paging"
    SERVICE_REQUEST = "service_request"
    DETACH = "detach"


class ResultType(Enum):
    """Resultado del evento."""
    SUCCESS = "success"
    FAILURE = "failure"


class RATType(Enum):
    """Radio Access Technology."""
    LTE = "LTE"
    FIVE_G = "5G"
    THREE_G = "3G"


# Configuración de probabilidades
EVENT_DISTRIBUTION = {
    EventType.ATTACH: 0.35,
    EventType.HANDOVER: 0.25,
    EventType.PAGING: 0.20,
    EventType.SERVICE_REQUEST: 0.15,
    EventType.DETACH: 0.05,
}

# Success rates realistas por tipo de evento
SUCCESS_RATES = {
    EventType.ATTACH: 0.97,
    EventType.HANDOVER: 0.98,
    EventType.PAGING: 0.94,
    EventType.SERVICE_REQUEST: 0.96,
    EventType.DETACH: 0.99,
}

# Causas de fallo por tipo de evento
FAILURE_CAUSES = {
    EventType.ATTACH: [
        "auth_failed",
        "timeout",
        "network_congestion",
        "invalid_credentials",
        "hsn_failure"
    ],
    EventType.HANDOVER: [
        "weak_signal",
        "target_cell_congestion",
        "timeout",
        "preparation_failure",
        "radio_link_failure"
    ],
    EventType.PAGING: [
        "no_response",
        "ue_unreachable",
        "timeout",
        "paging_overload"
    ],
    EventType.SERVICE_REQUEST: [
        "authentication_failure",
        "service_not_allowed",
        "congestion",
        "resource_unavailable"
    ],
    EventType.DETACH: [
        "abnormal_release",
        "timeout",
        "power_off"
    ],
}

# Bandas de frecuencia comunes
FREQUENCY_BANDS = ["B3", "B7", "B20", "B28", "B1", "B8"]

# Configuración de red
NETWORK_CONFIG = {
    "num_cells": 50,
    "num_enodebs": 10,
    "num_mmes": 2,
    "num_tracking_areas": 5,
}


# =====================================================================
# MODELOS DE DATOS
# =====================================================================

@dataclass
class SignalingEvent:
    """Representa un evento de señalización móvil."""
    event_id: str
    timestamp: str
    event_type: str
    result: str
    failure_cause: Optional[str]
    
    # Identificadores (anonimizados/hasheados)
    imsi_hash: str
    imei_hash: str
    
    # Elementos de red
    cell_id: str
    enodeb_id: str
    mme_id: str
    tracking_area: str
    
    # Detalles técnicos
    duration_ms: int
    rat_type: str
    frequency_band: str
    
    def to_dict(self) -> Dict:
        """Convierte el evento a diccionario."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convierte el evento a JSON."""
        return json.dumps(self.to_dict(), indent=2)


# =====================================================================
# GENERADOR DE EVENTOS
# =====================================================================

class TelecomEventGenerator:
    """Generador de eventos sintéticos de señalización móvil."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Inicializa el generador.
        
        Args:
            seed: Semilla para reproducibilidad (opcional)
        """
        self.logger = self._setup_logger()
        
        if seed:
            random.seed(seed)
            self.logger.info(f"Generador inicializado con seed: {seed}")
        else:
            self.logger.info("Generador inicializado sin seed")
        
        self.event_counter = 0
    
    def _setup_logger(self) -> logging.Logger:
        """Configura el logger."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        return logger
    
    def _is_peak_hour(self, hour: int) -> bool:
        """
        Determina si una hora es hora pico.
        
        Args:
            hour: Hora del día (0-23)
            
        Returns:
            True si es hora pico
        """
        # Horas pico: 8-10am, 12-2pm, 6-9pm
        return hour in [8, 9, 12, 13, 18, 19, 20]
    
    def _generate_event_type(self) -> EventType:
        """
        Selecciona un tipo de evento según distribución.
        
        Returns:
            EventType seleccionado
        """
        event_types = list(EVENT_DISTRIBUTION.keys())
        weights = list(EVENT_DISTRIBUTION.values())
        return random.choices(event_types, weights=weights)[0]
    
    def _determine_result(self, event_type: EventType) -> tuple[ResultType, Optional[str]]:
        """
        Determina si el evento es exitoso o fallido.
        
        Args:
            event_type: Tipo de evento
            
        Returns:
            Tuple de (resultado, causa_fallo)
        """
        success_rate = SUCCESS_RATES[event_type]
        is_success = random.random() < success_rate
        
        if is_success:
            return ResultType.SUCCESS, None
        else:
            failure_cause = random.choice(FAILURE_CAUSES[event_type])
            return ResultType.FAILURE, failure_cause
    
    def _generate_duration(self, is_success: bool) -> int:
        """
        Genera duración del evento en milisegundos.
        
        Args:
            is_success: Si el evento fue exitoso
            
        Returns:
            Duración en ms
        """
        if is_success:
            # Eventos exitosos: 100-500ms
            return random.randint(100, 500)
        else:
            # Eventos fallidos toman más tiempo
            return random.randint(500, 3000)
    
    def generate_event(self, base_timestamp: Optional[datetime] = None) -> SignalingEvent:
        """
        Genera un solo evento de señalización.
        
        Args:
            base_timestamp: Timestamp base (default: ahora)
            
        Returns:
            SignalingEvent generado
        """
        if base_timestamp is None:
            base_timestamp = datetime.now()
        
        # Agregar variación dentro del segundo
        timestamp = base_timestamp + timedelta(microseconds=random.randint(0, 999999))
        
        # Generar tipo de evento y resultado
        event_type = self._generate_event_type()
        result, failure_cause = self._determine_result(event_type)
        
        # Generar ID único
        self.event_counter += 1
        event_id = f"{timestamp.strftime('%Y%m%d%H%M%S')}_{self.event_counter:08d}"
        
        # Generar evento
        event = SignalingEvent(
            event_id=event_id,
            timestamp=timestamp.isoformat(),
            event_type=event_type.value,
            result=result.value,
            failure_cause=failure_cause,
            
            # Identificadores hasheados
            imsi_hash=f"IMSI_{random.randint(100000000, 999999999)}",
            imei_hash=f"IMEI_{random.randint(100000000, 999999999)}",
            
            # Elementos de red
            cell_id=f"CELL_{random.randint(1, NETWORK_CONFIG['num_cells']):03d}",
            enodeb_id=f"ENB_{random.randint(1, NETWORK_CONFIG['num_enodebs']):03d}",
            mme_id=f"MME_{random.randint(1, NETWORK_CONFIG['num_mmes']):02d}",
            tracking_area=f"TA_{random.randint(1, NETWORK_CONFIG['num_tracking_areas'])}",
            
            # Detalles técnicos
            duration_ms=self._generate_duration(result == ResultType.SUCCESS),
            rat_type=random.choice([rat.value for rat in RATType]),
            frequency_band=random.choice(FREQUENCY_BANDS),
        )
        
        return event
    
    def generate_batch(self, num_events: int, base_timestamp: Optional[datetime] = None) -> List[SignalingEvent]:
        """
        Genera un lote de eventos.
        
        Args:
            num_events: Número de eventos a generar
            base_timestamp: Timestamp base (default: ahora)
            
        Returns:
            Lista de eventos generados
        """
        self.logger.info(f"Generando batch de {num_events} eventos...")
        
        events = []
        for _ in range(num_events):
            event = self.generate_event(base_timestamp)
            events.append(event)
        
        self.logger.info(f"Batch generado: {num_events} eventos")
        return events
    
    def save_to_json(self, events: List[SignalingEvent], filepath: Path):
        """
        Guarda eventos a archivo JSON.
        
        Args:
            events: Lista de eventos
            filepath: Ruta del archivo
        """
        self.logger.info(f"Guardando {len(events)} eventos en {filepath}")
        
        # Crear directorio si no existe
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir eventos a dict
        events_dict = [event.to_dict() for event in events]
        
        # Guardar
        with open(filepath, 'w') as f:
            json.dump(events_dict, f, indent=2)
        
        self.logger.info(f"Eventos guardados exitosamente")
    
    def save_to_csv(self, events: List[SignalingEvent], filepath: Path):
        """
        Guarda eventos a archivo CSV.
        
        Args:
            events: Lista de eventos
            filepath: Ruta del archivo
        """
        self.logger.info(f"Guardando {len(events)} eventos en {filepath}")
        
        # Crear directorio si no existe
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir a DataFrame y guardar
        import pandas as pd
        df = pd.DataFrame([event.to_dict() for event in events])
        df.to_csv(filepath, index=False)
        
        self.logger.info(f"Eventos guardados exitosamente")
    
    def run_continuous(self, batch_size: int = 1000, interval_seconds: int = 60, 
                      output_dir: Path = Path("data/raw")):
        """
        Ejecuta el generador continuamente.
        
        Args:
            batch_size: Tamaño del batch
            interval_seconds: Intervalo entre batches (segundos)
            output_dir: Directorio de salida
        """
        self.logger.info(f"Iniciando modo continuo: {batch_size} eventos cada {interval_seconds}s")
        
        batch_num = 0
        try:
            while True:
                batch_num += 1
                timestamp = datetime.now()
                
                # Generar batch
                events = self.generate_batch(batch_size, timestamp)
                
                # Guardar con timestamp en nombre
                filename = f"events_{timestamp.strftime('%Y%m%d_%H%M%S')}_batch{batch_num:04d}.json"
                filepath = output_dir / filename
                
                self.save_to_json(events, filepath)
                
                # Esperar intervalo
                self.logger.info(f"Esperando {interval_seconds}s hasta próximo batch...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("\nGeneración continua detenida por usuario")
            self.logger.info(f"Total de batches generados: {batch_num}")


# =====================================================================
# CLI
# =====================================================================

def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Generador de eventos sintéticos de señalización móvil (SGSN-MME)"
    )
    
    parser.add_argument(
        '--mode',
        choices=['once', 'continuous'],
        default='once',
        help='Modo de ejecución: once (una vez) o continuous (continuo)'
    )
    
    parser.add_argument(
        '--events',
        type=int,
        default=10000,
        help='Número de eventos a generar (modo once)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Tamaño del batch (modo continuous)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Intervalo en segundos entre batches (modo continuous)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Directorio de salida'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Formato de salida (solo modo once)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Semilla para reproducibilidad (opcional)'
    )
    
    args = parser.parse_args()
    
    # Crear generador
    generator = TelecomEventGenerator(seed=args.seed)
    output_dir = Path(args.output_dir)
    
    if args.mode == 'once':
        # Generar una sola vez
        print(f"\n🚀 Generando {args.events} eventos...")
        events = generator.generate_batch(args.events)
        
        # Guardar según formato
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if args.format == 'json':
            filepath = output_dir / f"events_{timestamp}.json"
            generator.save_to_json(events, filepath)
        else:
            filepath = output_dir / f"events_{timestamp}.csv"
            generator.save_to_csv(events, filepath)
        
        print(f"✅ Eventos guardados en: {filepath}")
        
        # Mostrar estadísticas
        print("\n📊 Estadísticas:")
        event_types = {}
        results = {"success": 0, "failure": 0}
        
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            results[event.result] += 1
        
        print(f"  Total eventos: {len(events)}")
        print(f"  Exitosos: {results['success']} ({results['success']/len(events)*100:.1f}%)")
        print(f"  Fallidos: {results['failure']} ({results['failure']/len(events)*100:.1f}%)")
        print("\n  Por tipo de evento:")
        for event_type, count in sorted(event_types.items()):
            print(f"    {event_type}: {count} ({count/len(events)*100:.1f}%)")
    
    else:
        # Modo continuo
        print(f"\n🔄 Iniciando generación continua...")
        print(f"   Batch size: {args.batch_size} eventos")
        print(f"   Intervalo: {args.interval} segundos")
        print(f"   Output: {output_dir}")
        print("\n   Presiona Ctrl+C para detener\n")
        
        generator.run_continuous(
            batch_size=args.batch_size,
            interval_seconds=args.interval,
            output_dir=output_dir
        )


if __name__ == "__main__":
    main()