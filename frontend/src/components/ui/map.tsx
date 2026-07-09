import { createContext, forwardRef, useContext, useEffect, useImperativeHandle, useRef, useState, ReactNode } from "react";
import MapLibreGL from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const cn = (...classes: any[]) => classes.filter(Boolean).join(' ');

// ESRI Satellite Hybrid Style specification
const satelliteHybridStyle: MapLibreGL.StyleSpecification = {
  version: 8,
  sources: {
    satellite: {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
      ],
      tileSize: 256,
      attribution: "Tiles &copy; Esri"
    },
    labels: {
      type: "raster",
      tiles: [
        "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
      ],
      tileSize: 256,
      attribution: "Labels &copy; Esri"
    }
  },
  layers: [
    {
      id: "satellite-base",
      type: "raster",
      source: "satellite",
      minzoom: 0,
      maxzoom: 20
    },
    {
      id: "labels-overlay",
      type: "raster",
      source: "labels",
      minzoom: 0,
      maxzoom: 20
    }
  ]
};

type MapContextValue = {
  map: MapLibreGL.Map | null;
  isLoaded: boolean;
};

const MapContext = createContext<MapContextValue | null>(null);

export function useMap() {
  const context = useContext(MapContext);
  if (!context) {
    throw new Error("useMap must be used within a Map component");
  }
  return context;
}

export type MapViewport = {
  center: [number, number];
  zoom: number;
  bearing: number;
  pitch: number;
};

export type MapProps = {
  children?: ReactNode;
  className?: string;
  viewport?: Partial<MapViewport>;
  onViewportChange?: (viewport: MapViewport) => void;
  onClick?: (e: MapLibreGL.MapMouseEvent) => void;
};

export const Map = forwardRef<MapLibreGL.Map, MapProps>(function Map(
  { children, className, viewport, onViewportChange, onClick },
  ref
) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mapInstance, setMapInstance] = useState<MapLibreGL.Map | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  
  const onViewportChangeRef = useRef(onViewportChange);
  onViewportChangeRef.current = onViewportChange;

  const onClickRef = useRef(onClick);
  onClickRef.current = onClick;

  useImperativeHandle(ref, () => mapInstance as MapLibreGL.Map, [mapInstance]);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new MapLibreGL.Map({
      container: containerRef.current,
      style: satelliteHybridStyle,
      center: viewport?.center || [34.4534, -0.5298], // Default to Homa Bay
      zoom: viewport?.zoom || 15,
      pitch: viewport?.pitch || 0,
      bearing: viewport?.bearing || 0,
      attributionControl: false
    });

    map.on("load", () => {
      setIsLoaded(true);
    });

    map.on("move", () => {
      const center = map.getCenter();
      onViewportChangeRef.current?.({
        center: [center.lng, center.lat],
        zoom: map.getZoom(),
        bearing: map.getBearing(),
        pitch: map.getPitch()
      });
    });

    map.on("click", (e) => {
      onClickRef.current?.(e);
    });

    setMapInstance(map);

    return () => {
      map.remove();
      setMapInstance(null);
      setIsLoaded(false);
    };
  }, []);

  // Update center/zoom if changed from outside
  useEffect(() => {
    if (!mapInstance || !viewport) return;
    const currentCenter = mapInstance.getCenter();
    const targetCenter = viewport.center || [currentCenter.lng, currentCenter.lat];
    const targetZoom = viewport.zoom ?? mapInstance.getZoom();
    
    if (
      Math.abs(currentCenter.lng - targetCenter[0]) > 0.0001 ||
      Math.abs(currentCenter.lat - targetCenter[1]) > 0.0001 ||
      Math.abs(mapInstance.getZoom() - targetZoom) > 0.1
    ) {
      mapInstance.flyTo({
        center: targetCenter,
        zoom: targetZoom,
        duration: 1000
      });
    }
  }, [mapInstance, viewport]);

  return (
    <MapContext.Provider value={{ map: mapInstance, isLoaded }}>
      <div ref={containerRef} className={cn("relative h-full w-full overflow-hidden", className)}>
        {mapInstance && children}
      </div>
    </MapContext.Provider>
  );
});

export function MapControls({ position = "bottom-right" }: { position?: "top-left" | "top-right" | "bottom-left" | "bottom-right" }) {
  const { map } = useMap();
  
  useEffect(() => {
    if (!map) return;
    const nav = new MapLibreGL.NavigationControl({ showCompass: true });
    map.addControl(nav, position);
    return () => {
      try {
        if (map && map.getContainer()) {
          map.removeControl(nav);
        }
      } catch (e) {
        // ignore errors during unmount cleanup
      }
    };
  }, [map, position]);

  return null;
}

export type MapMarkerProps = {
  longitude: number;
  latitude: number;
  onClick?: (e: MouseEvent) => void;
  color?: string;
};

export function MapMarker({ longitude, latitude, onClick, color = "#659A5F" }: MapMarkerProps) {
  const { map } = useMap();
  const markerRef = useRef<MapLibreGL.Marker | null>(null);
  const elementRef = useRef<HTMLDivElement | null>(null);

  const onClickRef = useRef(onClick);
  onClickRef.current = onClick;

  useEffect(() => {
    if (!map) return;

    const el = document.createElement("div");
    el.style.width = "12px";
    el.style.height = "12px";
    el.style.borderRadius = "50%";
    el.style.backgroundColor = color;
    el.style.border = "2px solid white";
    el.style.boxShadow = "0 0 6px rgba(0,0,0,0.5)";
    el.style.cursor = "pointer";

    elementRef.current = el;

    const marker = new MapLibreGL.Marker({ element: el })
      .setLngLat([longitude, latitude])
      .addTo(map);

    markerRef.current = marker;

    const clickListener = (e: MouseEvent) => {
      onClickRef.current?.(e);
    };

    el.addEventListener("click", clickListener);

    return () => {
      try {
        if (map && map.getContainer()) {
          marker.remove();
        }
      } catch (e) {
        // ignore errors during unmount cleanup
      }
      markerRef.current = null;
      el.removeEventListener("click", clickListener);
    };
  }, [map, color]);

  useEffect(() => {
    if (markerRef.current) {
      markerRef.current.setLngLat([longitude, latitude]);
    }
  }, [longitude, latitude]);

  return null;
}

export type MapGeoJSONProps = {
  id?: string;
  data: any;
  fillPaint?: any;
  linePaint?: any;
};

export function MapGeoJSON({ id = "geojson-layer", data, fillPaint, linePaint }: MapGeoJSONProps) {
  const { map, isLoaded } = useMap();

  useEffect(() => {
    if (!map || !isLoaded || !data) return;

    const sourceId = `${id}-source`;
    const fillLayerId = `${id}-fill`;
    const lineLayerId = `${id}-line`;

    map.addSource(sourceId, {
      type: "geojson",
      data: data
    });

    if (fillPaint !== false) {
      map.addLayer({
        id: fillLayerId,
        type: "fill",
        source: sourceId,
        paint: fillPaint || {
          "fill-color": "#659A5F",
          "fill-opacity": 0.2
        }
      });
    }

    if (linePaint !== false) {
      map.addLayer({
        id: lineLayerId,
        type: "line",
        source: sourceId,
        paint: linePaint || {
          "line-color": "#659A5F",
          "line-width": 2
        }
      });
    }

    return () => {
      try {
        if (map && map.getContainer()) {
          if (map.getLayer(fillLayerId)) map.removeLayer(fillLayerId);
          if (map.getLayer(lineLayerId)) map.removeLayer(lineLayerId);
          if (map.getSource(sourceId)) map.removeSource(sourceId);
        }
      } catch (e) {
        // ignore errors during unmount cleanup
      }
    };
  }, [map, isLoaded, id, data, fillPaint, linePaint]);

  return null;
}

export type MapRouteProps = {
  id?: string;
  coordinates: [number, number][];
  color?: string;
  width?: number;
  opacity?: number;
  dashArray?: number[];
};

export function MapRoute({ id = "route-layer", coordinates, color = "#EAD35B", width = 3, opacity = 0.8, dashArray }: MapRouteProps) {
  const { map, isLoaded } = useMap();

  useEffect(() => {
    if (!map || !isLoaded || coordinates.length === 0) return;

    const sourceId = `${id}-source`;
    const lineLayerId = `${id}-line`;

    const geojson: any = {
      type: "Feature",
      properties: {},
      geometry: {
        type: "LineString",
        coordinates: coordinates
      }
    };

    map.addSource(sourceId, {
      type: "geojson",
      data: geojson
    });

    const paintSpec: any = {
      "line-color": color,
      "line-width": width,
      "line-opacity": opacity
    };

    const layoutSpec: any = {
      "line-join": "round",
      "line-cap": "round"
    };

    map.addLayer({
      id: lineLayerId,
      type: "line",
      source: sourceId,
      layout: layoutSpec,
      paint: paintSpec
    });

    if (dashArray && dashArray.length > 0) {
      map.setPaintProperty(lineLayerId, "line-dasharray", dashArray);
    }

    return () => {
      try {
        if (map && map.getContainer()) {
          if (map.getLayer(lineLayerId)) map.removeLayer(lineLayerId);
          if (map.getSource(sourceId)) map.removeSource(sourceId);
        }
      } catch (e) {
        // ignore errors during unmount cleanup
      }
    };
  }, [map, isLoaded, id, coordinates, color, width, opacity, dashArray]);

  return null;
}
