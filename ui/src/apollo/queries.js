import gql from "graphql-tag";

const projectFragment = gql`
  fragment projectFields on ProjectType {
    id
    name
    title
    ecosystem {
      id
      name
    }
    parentProject {
      id
      name
      parentProject {
        id
        name
        parentProject {
          id
          name
        }
      }
    }
  }
`;

const datasetFragment = gql`
  fragment datasetFields on DatasetType {
    datasource {
      type {
        name
      }
      uri
    }
    id
    filters
    category
    isArchived
  }
`;

const GET_ECOSYSTEMS = gql`
  query GetEcosystems($pageSize: Int, $page: Int) {
    ecosystems(pageSize: $pageSize, page: $page) {
      entities {
        id
        name
        title
        description
        projectSet {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
              subprojects {
                ...projectFields
              }
            }
          }
        }
      }
      pageInfo {
        totalResults
      }
    }
  }
  ${projectFragment}
`;

const GET_ECOSYSTEM_BY_ID = gql`
  query GetEcosystemByID($id: ID) {
    ecosystems(filters: { id: $id }, page: 1, pageSize: 1) {
      entities {
        name
        title
        description
        projectSet {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
              subprojects {
                ...projectFields
              }
            }
          }
        }
      }
    }
  }
  ${projectFragment}
`;

const GET_BASIC_PROJECT_INFO = gql`
  query GetBasicInfo($pageSize: Int, $page: Int, $filters: ProjectFilterType) {
    projects(pageSize: $pageSize, page: $page, filters: $filters) {
      entities {
        id
        title
        name
      }
    }
  }
`;

const GET_PROJECTS = gql`
  query GetProjects($pageSize: Int, $page: Int, $filters: ProjectFilterType) {
    projects(pageSize: $pageSize, page: $page, filters: $filters) {
      entities {
        ...projectFields
        subprojects {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
            }
          }
        }
      }
      pageInfo {
        page
        numPages
      }
    }
  }
  ${projectFragment}
`;

const GET_PROJECT_BY_NAME = gql`
  query getProjectById($filters: ProjectFilterType) {
    projects(pageSize: 1, page: 1, filters: $filters) {
      entities {
        ...projectFields
        datasetSet {
          ...datasetFields
        }
        subprojects {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
            }
          }
        }
      }
    }
  }
  ${projectFragment}
  ${datasetFragment}
`;

const GET_DATASET_BY_URI = gql`
  query getDatasetsByUri($projectId: ID!, $uri: String!) {
    datasets(filters: { uri: $uri, projectId: $projectId }) {
      entities {
        id
        category
        filters
        isArchived
        archivedAt
        datasource {
          type {
            name
          }
          uri
        }
        project {
          ...projectFields
        }
      }
    }
  }
  ${projectFragment}
`;

const GET_JOB = gql`
  query getJob($jobId: String!) {
    job(jobId: $jobId) {
      status
      result {
        ... on GitHubRepoResultType {
          url
          fork
          hasIssues
        }
      }
      errors
      jobId
      jobType
    }
  }
`;

const GET_DATASOURCE_CREDENTIALS = gql`
  query getDatasourceCredentials($datasource: ID) {
    credentials(filters: { datasourceName: $datasource }) {
      entities {
        token
      }
    }
  }
`;

const GET_USER_CREDENTIALS = gql`
  query getUserCredentials($page: Int, $pageSize: Int) {
    credentials(page: $page, pageSize: $pageSize) {
      entities {
        createdAt
        id
        name
        datasource {
          name
        }
      }
      pageInfo {
        page
        pageSize
        numPages
        totalResults
      }
    }
  }
`;

const getEcosystems = (apollo, pageSize, page) => {
  const response = apollo.query({
    query: GET_ECOSYSTEMS,
    variables: {
      pageSize,
      page
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

const getEcosystemByID = (apollo, id) => {
  const response = apollo.query({
    query: GET_ECOSYSTEM_BY_ID,
    variables: {
      id: id
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

const getBasicProjectInfo = (apollo, pageSize, page, filters) => {
  const response = apollo.query({
    query: GET_BASIC_PROJECT_INFO,
    variables: {
      pageSize,
      page,
      filters
    }
  });
  return response;
};

const getProjects = (apollo, pageSize, page, filters) => {
  const response = apollo.query({
    query: GET_PROJECTS,
    variables: {
      pageSize,
      page,
      filters
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

const getProjectByName = (apollo, name, ecosystemId) => {
  const response = apollo.query({
    query: GET_PROJECT_BY_NAME,
    variables: {
      filters: {
        ecosystemId: ecosystemId,
        name: name
      }
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

const getDatasetsByUri = (apollo, projectId, uri) => {
  const response = apollo.query({
    query: GET_DATASET_BY_URI,
    variables: {
      projectId: projectId,
      uri: uri
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

const getJob = (apollo, jobId) => {
  const response = apollo.query({
    query: GET_JOB,
    variables: {
      jobId: jobId
    }
  });
  return response;
};

const getDatasourceCredentials = (apollo, datasource) => {
  const response = apollo.query({
    query: GET_DATASOURCE_CREDENTIALS,
    variables: {
      datasource: datasource
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

const getUserCredentials = (apollo, page, pageSize) => {
  const response = apollo.query({
    query: GET_USER_CREDENTIALS,
    variables: {
      pageSize,
      page
    },
    fetchPolicy: "no-cache"
  });
  return response;
};

export {
  getDatasetsByUri,
  getEcosystems,
  getEcosystemByID,
  getBasicProjectInfo,
  getProjects,
  getProjectByName,
  getJob,
  GET_JOB,
  getDatasourceCredentials,
  getUserCredentials
};
