import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const NivelBadge = ({ nivel }) => {
    const colors = {
        oro: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        plata: 'bg-gray-100 text-gray-800 border-gray-300',
        bronce: 'bg-orange-100 text-orange-800 border-orange-300',
        descarte: 'bg-red-100 text-red-800 border-red-300'
    };

    const icons = {
        oro: '🥇',
        plata: '🥈',
        bronce: '🥉',
        descarte: '❌'
    };

    return (
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${colors[nivel] || colors.descarte}`}>
            {icons[nivel]} {nivel}
        </span>
    );
};

const EstadoBadge = ({ estado }) => {
    const colors = {
        nueva: 'bg-blue-100 text-blue-800',
        revisada: 'bg-purple-100 text-purple-800',
        en_preparacion: 'bg-yellow-100 text-yellow-800',
        enviada: 'bg-green-100 text-green-800',
        adjudicada: 'bg-green-200 text-green-900',
        no_adjudicada: 'bg-red-100 text-red-800',
        contactando: 'bg-indigo-100 text-indigo-800',
        convertida: 'bg-emerald-100 text-emerald-800',
        descartada: 'bg-gray-100 text-gray-600'
    };

    return (
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[estado] || 'bg-gray-100'}`}>
            {estado?.replace('_', ' ')}
        </span>
    );
};

const formatImporte = (importe) => {
    if (!importe) return '-';
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        maximumFractionDigits: 0
    }).format(importe);
};

const OportunidadesTable = ({
    oportunidades,
    loading,
    onUpdateEstado,
    onAsignar,
    tipo = 'licitacion',
    showSector = false,
    currentUserId
}) => {
    const navigate = useNavigate();
    const [selectedRows, setSelectedRows] = useState([]);

    const toggleSelect = (expediente) => {
        setSelectedRows(prev =>
            prev.includes(expediente)
                ? prev.filter(e => e !== expediente)
                : [...prev, expediente]
        );
    };

    const toggleSelectAll = () => {
        if (selectedRows.length === oportunidades.length) {
            setSelectedRows([]);
        } else {
            setSelectedRows(oportunidades.map(o => o.expediente));
        }
    };

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Cargando oportunidades...</p>
            </div>
        );
    }

    if (!oportunidades || oportunidades.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-gray-500">No se encontraron oportunidades con los filtros actuales.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-3 text-left">
                                <input
                                    type="checkbox"
                                    checked={selectedRows.length === oportunidades.length}
                                    onChange={toggleSelectAll}
                                    className="rounded border-gray-300"
                                />
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Título</th>
                            {showSector && (
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sector</th>
                            )}
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Importe</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                {tipo === 'licitacion' ? 'Días' : 'Adjudicatario'}
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asignado</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {oportunidades.map((op) => (
                            <tr
                                key={op.expediente}
                                className="hover:bg-gray-50 cursor-pointer"
                                onClick={() => navigate(`/oportunidad/${op.expediente}`)}
                            >
                                <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                                    <input
                                        type="checkbox"
                                        checked={selectedRows.includes(op.expediente)}
                                        onChange={() => toggleSelect(op.expediente)}
                                        className="rounded border-gray-300"
                                    />
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-lg">{op.scoring?.total || 0}</span>
                                        <NivelBadge nivel={op.scoring?.nivel || 'descarte'} />
                                    </div>
                                </td>
                                <td className="px-4 py-3">
                                    <div className="max-w-md">
                                        <p className="text-sm font-medium text-gray-900 truncate">{op.titulo}</p>
                                        <p className="text-xs text-gray-500 truncate">{op.organo_contratacion}</p>
                                    </div>
                                </td>
                                {showSector && (
                                    <td className="px-4 py-3">
                                        <span className="text-xs font-medium uppercase">{op.sector}</span>
                                    </td>
                                )}
                                <td className="px-4 py-3 text-sm">{formatImporte(op.importe)}</td>
                                <td className="px-4 py-3">
                                    {tipo === 'licitacion' ? (
                                        <span className={`text-sm font-medium ${op.dias_restantes <= 7 ? 'text-red-600' :
                                                op.dias_restantes <= 14 ? 'text-yellow-600' : 'text-gray-600'
                                            }`}>
                                            {op.dias_restantes != null ? `${op.dias_restantes}d` : '-'}
                                        </span>
                                    ) : (
                                        <span className="text-sm text-gray-600 truncate block max-w-32">
                                            {op.adjudicatario?.nombre || '-'}
                                        </span>
                                    )}
                                </td>
                                <td className="px-4 py-3">
                                    <EstadoBadge estado={op.estado} />
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-600">
                                    {op.propietario_nombre || '-'}
                                </td>
                                <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                                    <div className="flex gap-2">
                                        {!op.propietario && (
                                            <button
                                                onClick={() => onAsignar(op.expediente, currentUserId)}
                                                className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                                            >
                                                Tomar
                                            </button>
                                        )}
                                        {op.url_licitacion && (
                                            <a
                                                href={op.url_licitacion}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200"
                                            >
                                                PLACSP
                                            </a>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {selectedRows.length > 0 && (
                <div className="bg-gray-50 px-4 py-3 border-t flex items-center gap-4">
                    <span className="text-sm text-gray-600">{selectedRows.length} seleccionadas</span>
                    <button
                        onClick={() => setSelectedRows([])}
                        className="text-sm text-gray-500 hover:text-gray-700"
                    >
                        Limpiar selección
                    </button>
                </div>
            )}
        </div>
    );
};

export default OportunidadesTable;
