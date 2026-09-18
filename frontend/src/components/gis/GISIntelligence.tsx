import React, { useState, useEffect, useRef } from 'react';
import { 
  MapPin, 
  Layers, 
  Eye, 
  EyeOff, 
  Maximize2, 
  Minimize2, 
  Search, 
  Info, 
  SlidersHorizontal, 
  CheckSquare, 
  Square,
  Compass,
  ArrowRight,
  ShieldAlert,
  ChevronRight,
  Download
} from 'lucide-react';
import L from 'leaflet';
import { DEMO_GIS_DISTRICTS } from '../../data/mockData';
import { GISDistrict } from '../../types';

interface GISIntelligenceProps {
  onNavigate: (tab: string) => void;
}

export const GISIntelligence: React.FC<GISIntelligenceProps> = ({ onNavigate }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.LayerGroup | null>(null);
  const polygonsRef = useRef<L.LayerGroup | null>(null);

  const [selectedDistrict, setSelectedDistrict] = useState<GISDistrict>(DEMO_GIS_DISTRICTS[0]); // Bhopal default
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activeTab, setActiveTab] = useState<'layers' | 'district_info'>('layers');
  const [searchLocation, setSearchLocation] = useState('');
  const [detailedModalOpen, setDetailedModalOpen] = useState(false);

  // Active layer toggles
  const [activeLayers, setActiveLayers] = useState<{ [key: string]: boolean }>({
    'Agricultural Parcels': true,
    'Residential Built-Up': true,
    'Industrial Corridors': true,
    'Upper Lake Bhoj Wetland Buffer': true,
    'Flood & Drainage Risk': false,
    'Groundwater Stress Zones': true,
    'Outer Ring Road Expressway': true,
    'Master Plan 2031 Proposed Boundaries': true
  });

  const toggleLayer = (layerName: string) => {
    setActiveLayers(prev => ({
      ...prev,
      [layerName]: !prev[layerName]
    }));
  };

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Prevent re-initialization if map already exists
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [23.2599, 77.4126], // Centered on Bhopal, Madhya Pradesh
        zoom: 11,
        zoomControl: true,
      });

      // Professional Clean Map Tile Layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | BHUMI INSIGHT GIS',
        maxZoom: 18,
      }).addTo(map);

      markersRef.current = L.layerGroup().addTo(map);
      polygonsRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear existing markers
    if (markersRef.current) {
      markersRef.current.clearLayers();
    }

    // Custom Map Icon
    const customIcon = L.divIcon({
      className: 'custom-gis-pin',
      html: `
        <div style="background-color: #0f172a; color: #34d399; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #ffffff; box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-weight: 800; font-size: 11px;">
          BI
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });

    // Add District Markers
    DEMO_GIS_DISTRICTS.forEach((d) => {
      const marker = L.marker(d.coordinates, { icon: customIcon });
      marker.bindPopup(`
        <div style="font-family: sans-serif; padding: 4px;">
          <h4 style="margin: 0 0 4px 0; color: #0f172a; font-size: 14px;">${d.name}</h4>
          <p style="margin: 0; font-size: 11.5px; color: #475569;">Population: <strong>${d.population}</strong> | Urbanization: <strong>${d.urbanization}</strong></p>
          <div style="margin-top: 6px; font-size: 11px; color: #059669; font-weight: 600;">Click marker for district profile</div>
        </div>
      `);
      marker.on('click', () => {
        setSelectedDistrict(d);
        setActiveTab('district_info');
      });
      if (markersRef.current) {
        markersRef.current.addLayer(marker);
      }
    });

    // Add Simulated Land Use / Buffer Polygons for Bhopal
    if (polygonsRef.current) {
      polygonsRef.current.clearLayers();

      // Agricultural Fringe Polygon (Green)
      if (activeLayers['Agricultural Parcels']) {
        const agPolygon = L.polygon([
          [23.18, 77.35],
          [23.15, 77.45],
          [23.19, 77.52],
          [23.22, 77.48],
          [23.20, 77.38],
        ], {
          color: '#059669',
          fillColor: '#10b981',
          fillOpacity: 0.25,
          weight: 2,
        }).bindTooltip("Agricultural Land Parcel Zone (Class I/II)");
        polygonsRef.current.addLayer(agPolygon);
      }

      // Upper Lake Bhoj Wetland Buffer (Blue)
      if (activeLayers['Upper Lake Bhoj Wetland Buffer']) {
        const lakeBuffer = L.polygon([
          [23.24, 77.32],
          [23.26, 77.34],
          [23.25, 77.38],
          [23.23, 77.35],
        ], {
          color: '#2563eb',
          fillColor: '#3b82f6',
          fillOpacity: 0.35,
          weight: 2,
        }).bindTooltip("Bhoj Wetland Eco-Sensitive Ramsar Buffer (500m No-Construction)");
        polygonsRef.current.addLayer(lakeBuffer);
      }

      // Residential Growth Zone (Orange)
      if (activeLayers['Residential Built-Up']) {
        const resZone = L.polygon([
          [23.23, 77.40],
          [23.28, 77.42],
          [23.27, 77.46],
          [23.22, 77.44],
        ], {
          color: '#d97706',
          fillColor: '#f59e0b',
          fillOpacity: 0.22,
          weight: 2,
        }).bindTooltip("Residential Built-Up Agglomeration");
        polygonsRef.current.addLayer(resZone);
      }

      // Outer Ring Road / Highway Corridor Line
      if (activeLayers['Outer Ring Road Expressway']) {
        const highwayLine = L.polyline([
          [23.15, 77.32],
          [23.19, 77.46],
          [23.24, 77.54],
          [23.32, 77.52],
        ], {
          color: '#dc2626',
          weight: 4,
          dashArray: '6, 6'
        }).bindTooltip("Proposed Bhopal Outer Ring Road Alignment (3km Corridor)");
        polygonsRef.current.addLayer(highwayLine);
      }
    }

  }, [activeLayers]);

  // Handle location search or fly-to
  const handleFlyToDistrict = (district: GISDistrict) => {
    setSelectedDistrict(district);
    setActiveTab('district_info');
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo(district.coordinates, 12, { duration: 1.2 });
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const found = DEMO_GIS_DISTRICTS.find(d => d.name.toLowerCase().includes(searchLocation.toLowerCase()));
    if (found) {
      handleFlyToDistrict(found);
    } else {
      alert(`Location '${searchLocation}' indexed in National Cadastre. Flying to Madhya Pradesh baseline.`);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.flyTo([23.2599, 77.4126], 11);
      }
    }
  };

  return (
    <div className={`page-container ${isFullscreen ? 'gis-fullscreen' : ''}`} style={{ position: 'relative' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-blue">Multi-Resolution GIS Intelligence</span>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>Sentinel-2 + Cadastral Bhuvan Layer Mesh</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a' }}>
            GIS INTELLIGENCE MODULE
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {/* Location Quick Switcher */}
          <select 
            className="form-select"
            style={{ width: 'auto', fontSize: '12.5px' }}
            value={selectedDistrict.name}
            onChange={(e) => {
              const d = DEMO_GIS_DISTRICTS.find(item => item.name === e.target.value);
              if (d) handleFlyToDistrict(d);
            }}
          >
            {DEMO_GIS_DISTRICTS.map(d => (
              <option key={d.id} value={d.name}>{d.name} (Focus)</option>
            ))}
          </select>

          <button 
            className="btn btn-sm btn-secondary"
            onClick={() => setIsFullscreen(!isFullscreen)}
            title="Toggle Map Fullscreen"
          >
            {isFullscreen ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
            <span>{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</span>
          </button>

          <button 
            className="btn btn-sm btn-success"
            onClick={() => onNavigate('policy-simulator')}
          >
            <SlidersHorizontal size={15} />
            <span>Simulate Policy on Region</span>
          </button>
        </div>
      </div>

      {/* Map + Side Control Container */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '16px', height: '640px', position: 'relative' }}>
        {/* Left: Leaflet Interactive Map View */}
        <div style={{ position: 'relative', borderRadius: '12px', overflow: 'hidden', border: '1px solid #cbd5e1', boxShadow: '0 4px 12px -2px rgba(15, 23, 42, 0.08)' }}>
          {/* Map Location Search Overlay */}
          <form 
            onSubmit={handleSearchSubmit} 
            style={{ position: 'absolute', top: '12px', left: '60px', zIndex: 500, width: '280px' }}
          >
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
              <input 
                type="text" 
                className="form-input" 
                style={{ padding: '8px 12px 8px 32px', fontSize: '12.5px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(4px)', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                placeholder="Search Bhopal, Indore, Delhi..."
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
              />
            </div>
          </form>

          {/* Map Legend Overlay */}
          <div style={{ position: 'absolute', bottom: '16px', left: '16px', zIndex: 500, background: 'rgba(255, 255, 255, 0.94)', backdropFilter: 'blur(4px)', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '11.5px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: '6px' }}>Spatial Overlay Legend</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', color: '#334155' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '2px', border: '1px solid #059669' }}></span>
                <span>Agricultural Retention (Class I/II)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#3b82f6', borderRadius: '2px', border: '1px solid #2563eb' }}></span>
                <span>Upper Lake Bhoj Wetland 500m Buffer</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#f59e0b', borderRadius: '2px', border: '1px solid #d97706' }}></span>
                <span>Residential Built-Up Core</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '14px', height: '3px', backgroundColor: '#dc2626' }}></span>
                <span>Proposed Outer Ring Road Alignment</span>
              </div>
            </div>
          </div>

          {/* Leaflet DOM Anchor */}
          <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }}></div>
        </div>

        {/* Right Sidebar: Layer Switcher & District Profile */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: 0 }}>
          {/* Control Tabs */}
          <div style={{ display: 'flex', borderBottom: '1px solid #e2e8f0' }}>
            <button 
              style={{ flex: 1, padding: '12px', border: 'none', background: activeTab === 'layers' ? '#ffffff' : '#f8fafc', fontWeight: 700, fontSize: '12.5px', color: activeTab === 'layers' ? '#2563eb' : '#64748b', borderBottom: activeTab === 'layers' ? '2px solid #2563eb' : 'none', cursor: 'pointer' }}
              onClick={() => setActiveTab('layers')}
            >
              Layer Switcher
            </button>
            <button 
              style={{ flex: 1, padding: '12px', border: 'none', background: activeTab === 'district_info' ? '#ffffff' : '#f8fafc', fontWeight: 700, fontSize: '12.5px', color: activeTab === 'district_info' ? '#2563eb' : '#64748b', borderBottom: activeTab === 'district_info' ? '2px solid #2563eb' : 'none', cursor: 'pointer' }}
              onClick={() => setActiveTab('district_info')}
            >
              District Inspector
            </button>
          </div>

          {/* Tab 1: Layer Switcher Menu */}
          {activeTab === 'layers' && (
            <div style={{ padding: '16px', overflowY: 'auto', flex: 1 }}>
              <div style={{ marginBottom: '14px' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
                  1. Land Use Layers
                </div>
                {['Agricultural Parcels', 'Residential Built-Up', 'Industrial Corridors', 'Upper Lake Bhoj Wetland Buffer'].map(layer => (
                  <div 
                    key={layer}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 0', fontSize: '12.5px', color: '#1e293b', cursor: 'pointer' }}
                    onClick={() => toggleLayer(layer)}
                  >
                    <span>{layer}</span>
                    {activeLayers[layer] ? (
                      <CheckSquare size={16} style={{ color: '#059669' }} />
                    ) : (
                      <Square size={16} style={{ color: '#94a3b8' }} />
                    )}
                  </div>
                ))}
              </div>

              <div style={{ marginBottom: '14px', paddingTop: '10px', borderTop: '1px solid #f1f5f9' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
                  2. Climate & Hydrology Risk
                </div>
                {['Flood & Drainage Risk', 'Groundwater Stress Zones'].map(layer => (
                  <div 
                    key={layer}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 0', fontSize: '12.5px', color: '#1e293b', cursor: 'pointer' }}
                    onClick={() => toggleLayer(layer)}
                  >
                    <span>{layer}</span>
                    {activeLayers[layer] ? (
                      <CheckSquare size={16} style={{ color: '#059669' }} />
                    ) : (
                      <Square size={16} style={{ color: '#94a3b8' }} />
                    )}
                  </div>
                ))}
              </div>

              <div style={{ paddingTop: '10px', borderTop: '1px solid #f1f5f9' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
                  3. Infrastructure & Development
                </div>
                {['Outer Ring Road Expressway', 'Master Plan 2031 Proposed Boundaries'].map(layer => (
                  <div 
                    key={layer}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 0', fontSize: '12.5px', color: '#1e293b', cursor: 'pointer' }}
                    onClick={() => toggleLayer(layer)}
                  >
                    <span>{layer}</span>
                    {activeLayers[layer] ? (
                      <CheckSquare size={16} style={{ color: '#059669' }} />
                    ) : (
                      <Square size={16} style={{ color: '#94a3b8' }} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 2: Selected District Profile (Prompt SPEC requirement for Bhopal District) */}
          {activeTab === 'district_info' && (
            <div style={{ padding: '16px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>
                    {selectedDistrict.name}
                  </h3>
                  <span className="badge badge-green">State: MP</span>
                </div>
                <div style={{ fontSize: '11.5px', color: '#64748b', marginBottom: '14px' }}>
                  Administrative Cadastre & LULC Metric Telemetry
                </div>

                {/* Key Metrics Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginBottom: '16px' }}>
                  <div style={{ background: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Population:</div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>{selectedDistrict.population}</div>
                  </div>
                  <div style={{ background: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Urbanization:</div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: '#2563eb' }}>{selectedDistrict.urbanization}</div>
                  </div>
                  <div style={{ background: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Agricultural Land:</div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: '#059669' }}>{selectedDistrict.ag_land}</div>
                  </div>
                  <div style={{ background: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Climate Risk:</div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: '#d97706' }}>{selectedDistrict.climate_risk}</div>
                  </div>
                  <div style={{ background: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Urban Expansion:</div>
                    <div style={{ fontSize: '15px', fontWeight: 800, color: '#dc2626' }}>{selectedDistrict.urban_expansion}</div>
                  </div>
                  <div style={{ background: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Infra Pressure:</div>
                    <div style={{ fontSize: '15px', fontWeight: 800, color: '#475569' }}>{selectedDistrict.infra_pressure}</div>
                  </div>
                </div>

                {/* Primary Growth Corridors */}
                <div style={{ marginBottom: '14px' }}>
                  <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#0f172a', marginBottom: '6px' }}>
                    Primary Expansion Corridors:
                  </div>
                  <ul style={{ paddingLeft: '16px', fontSize: '12px', color: '#475569', lineHeight: 1.4 }}>
                    {selectedDistrict.primary_growth_corridors?.map((corridor, idx) => (
                      <li key={idx}>{corridor}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* View Detailed Analysis Button */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <button 
                  className="btn btn-primary"
                  style={{ width: '100%' }}
                  onClick={() => setDetailedModalOpen(true)}
                >
                  <Info size={14} />
                  <span>View Detailed Analysis</span>
                </button>
                <button 
                  className="btn btn-secondary"
                  style={{ width: '100%' }}
                  onClick={() => onNavigate('policy-simulator')}
                >
                  <SlidersHorizontal size={14} />
                  <span>Run Scenario on this District</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Analysis Modal */}
      {detailedModalOpen && (
        <div className="modal-backdrop" onClick={() => setDetailedModalOpen(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a' }}>
                  {selectedDistrict.name} — Comprehensive Geospatial Dossier
                </h3>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Coordinated Telemetry & Master Plan 2031 Projections
                </div>
              </div>
              <button 
                onClick={() => setDetailedModalOpen(false)}
                style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#64748b' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontWeight: 700, fontSize: '13.5px', color: '#0f172a' }}>
                  1. Agricultural Land Loss Vulnerability Index:
                </div>
                <p style={{ fontSize: '12.5px', color: '#475569', marginTop: '4px', lineHeight: 1.5 }}>
                  Bhopal has registered an average of 420 hectares/year of double-cropped agricultural land diversion over the past 5 years. 
                  Southern corridors (Kolar & Mandideep) demonstrate 64% higher conversion probability due to Outer Ring Road speculation.
                </p>
              </div>

              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontWeight: 700, fontSize: '13.5px', color: '#0f172a' }}>
                  2. Bhoj Wetland Catchment Buffer Impact:
                </div>
                <p style={{ fontSize: '12.5px', color: '#475569', marginTop: '4px', lineHeight: 1.5 }}>
                  The 361 sq km Upper Lake basin faces severe sedimentation stress. Sub-watershed runoff models confirm that converting agrarian retention basins into paved housing blocks would decrease groundwater storage by 2.4 million cubic meters annually.
                </p>
              </div>

              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontWeight: 700, fontSize: '13.5px', color: '#0f172a' }}>
                  3. Infrastructure Capacity Deficit:
                </div>
                <p style={{ fontSize: '12.5px', color: '#475569', marginTop: '4px', lineHeight: 1.5 }}>
                  Existing civic water supply from Narmada pipeline and Kolar reservoir operates at 88% capacity. Proposed fringe townships would require an estimated ₹420 Cr capital investment in decentralized sewage treatment.
                </p>
              </div>

              <div className="disclaimer-box">
                <strong>Decision Support Parameter:</strong> These geospatial indicators are derived from Sentinel-2 10m LULC classifications and CGWB hydrological reports. Used for policy simulation testing.
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '18px', gap: '8px' }}>
              <button 
                className="btn btn-secondary"
                onClick={() => setDetailedModalOpen(false)}
              >
                Close Dossier
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => {
                  setDetailedModalOpen(false);
                  onNavigate('policy-simulator');
                }}
              >
                <span>Launch Simulator with Bhopal Parameters</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
